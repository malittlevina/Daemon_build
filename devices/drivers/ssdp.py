from __future__ import annotations

from typing import Any
import socket
import time
from urllib.parse import urlparse

from devices.drivers.base import DiscoveryDriver
from devices.types import DevicePassport


class SsdpDiscoveryDriver(DiscoveryDriver):
    """
    SSDP/UPnP discovery (software-only) via M-SEARCH multicast.
    """

    name = "ssdp"

    def __init__(
        self,
        *,
        interval_s: float = 30.0,
        mx: int = 2,
        st: str = "ssdp:all",
        timeout_s: float = 3.0,
    ):
        super().__init__(interval_s=interval_s)
        self.mx = mx
        self.st = st
        self.timeout_s = timeout_s

    def scan_once(self) -> list[DevicePassport]:
        payload = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            'MAN: "ssdp:discover"\r\n'
            f"MX: {self.mx}\r\n"
            f"ST: {self.st}\r\n"
            "\r\n"
        ).encode("utf-8")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(self.timeout_s)
            sock.sendto(payload, ("239.255.255.250", 1900))

            passports: dict[str, DevicePassport] = {}
            deadline = time.time() + self.timeout_s

            while time.time() < deadline:
                try:
                    data, addr = sock.recvfrom(65535)
                except socket.timeout:
                    break

                ip = addr[0]
                headers = self._parse_ssdp_response(data)

                usn = headers.get("usn")
                st = headers.get("st") or headers.get("nt") or self.st
                location = headers.get("location")
                server = headers.get("server")

                identity: dict[str, Any] = {"ip": ip}
                if usn:
                    identity["usn"] = usn
                if location:
                    identity["location"] = location

                device_id = DevicePassport.derive_device_id(source=self.name, identity=identity)

                fingerprints: dict[str, Any] = {
                    "ssdp": {
                        "st": st,
                        "usn": usn,
                        "location": location,
                        "server": server,
                        "headers": headers,
                    }
                }

                caps: set[str] = {"transport.ip", "protocol.ssdp"}
                if server and any(x in server.lower() for x in ["upnp", "dlna"]):
                    caps.add("cap.media")
                if location:
                    parsed = urlparse(location)
                    if parsed.scheme in ("http", "https"):
                        caps.add("protocol.http")

                passport = DevicePassport(
                    device_id=device_id,
                    source=self.name,
                    identity=identity,
                    fingerprints=fingerprints,
                    capabilities=caps,
                    trust_state="seen",
                )

                passports[device_id] = passport

            return list(passports.values())
        finally:
            sock.close()

    @staticmethod
    def _parse_ssdp_response(packet: bytes) -> dict[str, str]:
        """
        Parse SSDP response headers. Keys are normalized to lowercase.
        """
        try:
            text = packet.decode("utf-8", errors="replace")
        except Exception:
            return {}
        lines = [ln.strip() for ln in text.split("\r\n") if ln.strip()]
        headers: dict[str, str] = {}
        for ln in lines[1:]:
            if ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            headers[k.strip().lower()] = v.strip()
        return headers

