from __future__ import annotations

from typing import Any
import os

from devices.drivers.base import DiscoveryDriver
from devices.types import DevicePassport


class ArpNeighborDriver(DiscoveryDriver):
    """
    Best-effort neighbor discovery from /proc/net/arp (IPv4).

    This is not "active scanning"; it simply surfaces neighbors already seen by
    the kernel ARP cache (useful as a low-permission, low-risk seed signal).
    """

    name = "arp"

    def __init__(self, *, interval_s: float = 60.0, arp_path: str = "/proc/net/arp"):
        super().__init__(interval_s=interval_s)
        self.arp_path = arp_path

    def scan_once(self) -> list[DevicePassport]:
        if not os.path.exists(self.arp_path):
            return []

        passports: list[DevicePassport] = []
        try:
            with open(self.arp_path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        except Exception:
            return []

        if len(lines) <= 1:
            return []

        # Header: IP address | HW type | Flags | HW address | Mask | Device
        for ln in lines[1:]:
            parts = ln.split()
            if len(parts) < 6:
                continue
            ip, hw_type, flags, mac, mask, iface = parts[:6]
            if mac.lower() in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"):
                continue

            identity: dict[str, Any] = {"ip": ip, "mac": mac.lower(), "iface": iface}
            device_id = DevicePassport.derive_device_id(source=self.name, identity={"mac": mac.lower(), "ip": ip})

            fingerprints = {"arp": {"hw_type": hw_type, "flags": flags, "mask": mask}}
            caps = {"transport.ip", "signal.arp"}

            passports.append(
                DevicePassport(
                    device_id=device_id,
                    source=self.name,
                    identity=identity,
                    fingerprints=fingerprints,
                    capabilities=caps,
                    trust_state="seen",
                )
            )

        return passports

