# devices/adapters/wifi_adapter.py
"""
WiFi Network Adapter
====================
Handles WiFi network device discovery using multiple methods:
- mDNS/Bonjour service discovery
- ARP scanning for local network devices
- SSDP/UPnP discovery for smart devices
- Network interface detection

Dependencies:
- zeroconf: For mDNS/Bonjour discovery
- scapy: For ARP scanning (optional, requires root)
- netifaces: For network interface info
"""

import socket
import threading
import time
import struct
import re
from typing import Dict, List, Optional, Callable, Any, Set
from .base_adapter import BaseProtocolAdapter, AdapterState

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from devices.device_registry import (
    Device, DeviceProtocol, DeviceState, DeviceCapability, DeviceMetadata
)


class WiFiAdapter(BaseProtocolAdapter):
    """
    WiFi network adapter for discovering devices on local networks.
    Uses mDNS, SSDP, and ARP scanning for comprehensive discovery.
    """
    
    # mDNS service types and their capabilities
    MDNS_SERVICES = {
        "_http._tcp.local.": [],
        "_https._tcp.local.": [],
        "_hap._tcp.local.": [DeviceCapability.SWITCH],  # HomeKit
        "_homekit._tcp.local.": [DeviceCapability.SWITCH],
        "_airplay._tcp.local.": [DeviceCapability.MEDIA_PLAYBACK, DeviceCapability.SPEAKER],
        "_raop._tcp.local.": [DeviceCapability.MEDIA_PLAYBACK, DeviceCapability.SPEAKER],
        "_spotify-connect._tcp.local.": [DeviceCapability.MEDIA_PLAYBACK],
        "_googlecast._tcp.local.": [DeviceCapability.MEDIA_PLAYBACK, DeviceCapability.DISPLAY],
        "_printer._tcp.local.": [],
        "_ipp._tcp.local.": [],
        "_smb._tcp.local.": [DeviceCapability.STORAGE, DeviceCapability.FILE_TRANSFER],
        "_afpovertcp._tcp.local.": [DeviceCapability.STORAGE, DeviceCapability.FILE_TRANSFER],
        "_nfs._tcp.local.": [DeviceCapability.STORAGE],
        "_ssh._tcp.local.": [DeviceCapability.COMPUTE],
        "_sftp-ssh._tcp.local.": [DeviceCapability.STORAGE, DeviceCapability.FILE_TRANSFER],
        "_mqtt._tcp.local.": [],
        "_hue._tcp.local.": [DeviceCapability.LED, DeviceCapability.DIMMER],
        "_matter._tcp.local.": [DeviceCapability.SWITCH],
        "_matter._udp.local.": [DeviceCapability.SWITCH],
        "_companion-link._tcp.local.": [],
        "_sleep-proxy._udp.local.": [],
    }
    
    # SSDP search targets
    SSDP_TARGETS = [
        "ssdp:all",
        "upnp:rootdevice",
        "urn:schemas-upnp-org:device:MediaRenderer:1",
        "urn:schemas-upnp-org:device:MediaServer:1",
        "urn:schemas-upnp-org:device:Basic:1",
        "urn:dial-multiscreen-org:service:dial:1",
    ]
    
    def __init__(self):
        super().__init__("WiFiAdapter")
        self._zeroconf_available = False
        self._scapy_available = False
        self._zeroconf = None
        self._browsers: List[Any] = []
        self._discovered_services: Dict[str, Dict] = {}
        self._scan_active = False
        self._discovered_ips: Set[str] = set()
        
    def initialize(self) -> bool:
        """Initialize WiFi adapter and check for available libraries."""
        self.state = AdapterState.INITIALIZING
        print(f"[{self.name}] Initializing...")
        
        # Try to import zeroconf for mDNS
        try:
            from zeroconf import Zeroconf, ServiceBrowser
            self._zeroconf_available = True
            print(f"[{self.name}] mDNS/Bonjour support available (zeroconf)")
        except ImportError:
            print(f"[{self.name}] zeroconf not installed. mDNS discovery unavailable.")
            print(f"[{self.name}] Install with: pip install zeroconf")
        
        # Try to import scapy for ARP scanning
        try:
            from scapy.all import ARP, Ether, srp
            self._scapy_available = True
            print(f"[{self.name}] ARP scanning support available (scapy)")
        except ImportError:
            print(f"[{self.name}] scapy not installed. ARP scanning unavailable.")
        
        # Check for network interfaces
        self._local_ip = self._get_local_ip()
        if self._local_ip:
            print(f"[{self.name}] Local IP: {self._local_ip}")
            self._is_available = True
        else:
            print(f"[{self.name}] Could not determine local IP")
            self._is_available = self._zeroconf_available
        
        if self._is_available:
            self.state = AdapterState.READY
            print(f"[{self.name}] Initialized successfully.")
        else:
            self.state = AdapterState.ERROR
            self._report_error("No network discovery methods available")
            
        return self._is_available
    
    def _get_local_ip(self) -> Optional[str]:
        """Get the local IP address."""
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None
    
    def _get_network_prefix(self) -> Optional[str]:
        """Get the network prefix (e.g., 192.168.1)."""
        if self._local_ip:
            parts = self._local_ip.rsplit('.', 1)
            return parts[0] if len(parts) == 2 else None
        return None
    
    class MDNSListener:
        """Listener for mDNS service discoveries."""
        
        def __init__(self, adapter: 'WiFiAdapter', callback: Callable):
            self.adapter = adapter
            self.callback = callback
        
        def add_service(self, zc, service_type, name):
            """Called when a service is discovered."""
            try:
                from zeroconf import Zeroconf
                
                info = zc.get_service_info(service_type, name)
                if info:
                    device = self.adapter._mdns_info_to_device(info, service_type)
                    if device:
                        self.callback(device)
            except Exception as e:
                print(f"[WiFiAdapter] mDNS service info error: {e}")
        
        def remove_service(self, zc, service_type, name):
            """Called when a service is removed."""
            pass
        
        def update_service(self, zc, service_type, name):
            """Called when a service is updated."""
            self.add_service(zc, service_type, name)
    
    def _mdns_info_to_device(self, info, service_type: str) -> Optional[Device]:
        """Convert mDNS service info to Device."""
        try:
            # Get IP addresses
            addresses = []
            if hasattr(info, 'addresses'):
                addresses = [socket.inet_ntoa(addr) for addr in info.addresses if len(addr) == 4]
            elif hasattr(info, 'parsed_addresses'):
                addresses = info.parsed_addresses()
            
            if not addresses:
                return None
            
            ip = addresses[0]
            
            # Generate device ID from IP + service
            device_id = f"wifi_{ip.replace('.', '_')}_{info.port}"
            
            # Get capabilities from service type
            capabilities = list(self.MDNS_SERVICES.get(service_type, []))
            
            # Parse properties
            properties = {}
            if hasattr(info, 'properties'):
                for key, value in info.properties.items():
                    if isinstance(key, bytes):
                        key = key.decode('utf-8', errors='ignore')
                    if isinstance(value, bytes):
                        value = value.decode('utf-8', errors='ignore')
                    properties[key] = value
            
            # Determine manufacturer from properties
            manufacturer = properties.get('manufacturer') or properties.get('vendor')
            model = properties.get('model') or properties.get('md')
            
            metadata = DeviceMetadata(
                manufacturer=manufacturer,
                model=model,
                firmware_version=properties.get('fw') or properties.get('firmware'),
                serial_number=properties.get('serialNumber') or properties.get('sn'),
                last_seen=time.time(),
                custom_data={
                    'service_type': service_type,
                    'port': info.port,
                    'properties': properties,
                    'all_addresses': addresses
                }
            )
            
            # Clean up the name
            name = info.name
            if name.endswith(service_type):
                name = name[:-len(service_type)].rstrip('.')
            
            return Device(
                id=device_id,
                name=name or f"Network Device {ip}",
                protocol=DeviceProtocol.WIFI,
                state=DeviceState.DISCOVERED,
                address=ip,
                capabilities=capabilities,
                metadata=metadata,
                services={service_type: {'port': info.port, 'properties': properties}}
            )
            
        except Exception as e:
            print(f"[WiFiAdapter] Error converting mDNS info: {e}")
            return None
    
    def _start_mdns_discovery(self, callback: Callable):
        """Start mDNS/Bonjour service discovery."""
        try:
            from zeroconf import Zeroconf, ServiceBrowser
            
            self._zeroconf = Zeroconf()
            listener = self.MDNSListener(self, callback)
            
            # Browse for all known service types
            for service_type in self.MDNS_SERVICES.keys():
                browser = ServiceBrowser(self._zeroconf, service_type, listener)
                self._browsers.append(browser)
            
            print(f"[{self.name}] mDNS discovery started for {len(self.MDNS_SERVICES)} service types")
            
        except Exception as e:
            self._report_error(f"mDNS discovery failed: {e}")
    
    def _stop_mdns_discovery(self):
        """Stop mDNS discovery."""
        if self._zeroconf:
            try:
                self._zeroconf.close()
            except Exception:
                pass
            self._zeroconf = None
        self._browsers.clear()
    
    def _ssdp_discover(self, callback: Callable, timeout: float = 5.0):
        """Discover UPnP/SSDP devices."""
        print(f"[{self.name}] Starting SSDP discovery...")
        
        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900
        
        for target in self.SSDP_TARGETS:
            if not self._scan_active:
                break
                
            try:
                msg = "\r\n".join([
                    "M-SEARCH * HTTP/1.1",
                    f"HOST: {SSDP_ADDR}:{SSDP_PORT}",
                    "MAN: \"ssdp:discover\"",
                    "MX: 2",
                    f"ST: {target}",
                    "", ""
                ]).encode('utf-8')
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout / len(self.SSDP_TARGETS))
                sock.sendto(msg, (SSDP_ADDR, SSDP_PORT))
                
                try:
                    while self._scan_active:
                        data, addr = sock.recvfrom(1024)
                        device = self._parse_ssdp_response(data.decode('utf-8'), addr[0])
                        if device and addr[0] not in self._discovered_ips:
                            self._discovered_ips.add(addr[0])
                            callback(device)
                except socket.timeout:
                    pass
                finally:
                    sock.close()
                    
            except Exception as e:
                pass  # Silent fail for individual SSDP targets
        
        print(f"[{self.name}] SSDP discovery complete")
    
    def _parse_ssdp_response(self, response: str, ip: str) -> Optional[Device]:
        """Parse SSDP response into Device."""
        try:
            lines = response.split('\r\n')
            headers = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.upper().strip()] = value.strip()
            
            # Get device info from headers
            server = headers.get('SERVER', '')
            location = headers.get('LOCATION', '')
            usn = headers.get('USN', '')
            
            device_id = f"ssdp_{ip.replace('.', '_')}"
            
            # Determine capabilities from USN
            capabilities = []
            if 'MediaRenderer' in usn:
                capabilities.extend([DeviceCapability.MEDIA_PLAYBACK, DeviceCapability.SPEAKER])
            if 'MediaServer' in usn:
                capabilities.extend([DeviceCapability.STORAGE, DeviceCapability.MEDIA_PLAYBACK])
            
            # Parse manufacturer from server string
            manufacturer = None
            if 'roku' in server.lower():
                manufacturer = 'Roku'
            elif 'samsung' in server.lower():
                manufacturer = 'Samsung'
            elif 'lg' in server.lower():
                manufacturer = 'LG'
            elif 'sony' in server.lower():
                manufacturer = 'Sony'
            
            metadata = DeviceMetadata(
                manufacturer=manufacturer,
                last_seen=time.time(),
                custom_data={
                    'server': server,
                    'location': location,
                    'usn': usn,
                    'ssdp_headers': headers
                }
            )
            
            # Try to extract a friendly name
            name = None
            if 'FRIENDLY-NAME' in headers:
                name = headers['FRIENDLY-NAME']
            
            return Device(
                id=device_id,
                name=name or f"UPnP Device {ip}",
                protocol=DeviceProtocol.WIFI,
                state=DeviceState.DISCOVERED,
                address=ip,
                capabilities=capabilities,
                metadata=metadata,
                services={'upnp': {'location': location, 'usn': usn}}
            )
            
        except Exception as e:
            return None
    
    def _arp_scan(self, callback: Callable, timeout: float = 5.0):
        """Scan local network using ARP."""
        if not self._scapy_available:
            return
        
        prefix = self._get_network_prefix()
        if not prefix:
            return
        
        print(f"[{self.name}] Starting ARP scan on {prefix}.0/24...")
        
        try:
            from scapy.all import ARP, Ether, srp, conf
            
            # Suppress scapy warnings
            conf.verb = 0
            
            target_ip = f"{prefix}.0/24"
            arp = ARP(pdst=target_ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            
            result = srp(packet, timeout=timeout, verbose=False)[0]
            
            for sent, received in result:
                if not self._scan_active:
                    break
                
                ip = received.psrc
                mac = received.hwsrc
                
                if ip not in self._discovered_ips:
                    self._discovered_ips.add(ip)
                    device = self._arp_to_device(ip, mac)
                    callback(device)
            
            print(f"[{self.name}] ARP scan complete. Found {len(result)} devices.")
            
        except PermissionError:
            print(f"[{self.name}] ARP scan requires root/admin privileges")
        except Exception as e:
            self._report_error(f"ARP scan failed: {e}")
    
    def _arp_to_device(self, ip: str, mac: str) -> Device:
        """Convert ARP response to Device."""
        manufacturer = self._lookup_mac_vendor(mac)
        
        metadata = DeviceMetadata(
            manufacturer=manufacturer,
            last_seen=time.time(),
            custom_data={'mac_address': mac}
        )
        
        return Device(
            id=f"arp_{mac.replace(':', '_')}",
            name=f"Network Device {ip}" if not manufacturer else f"{manufacturer} Device",
            protocol=DeviceProtocol.WIFI,
            state=DeviceState.DISCOVERED,
            address=ip,
            capabilities=[],
            metadata=metadata
        )
    
    def _lookup_mac_vendor(self, mac: str) -> Optional[str]:
        """Lookup manufacturer from MAC address OUI."""
        # Common OUI prefixes
        OUI_PREFIXES = {
            "00:1A:79": "Apple",
            "00:03:93": "Apple",
            "00:0A:95": "Apple",
            "00:17:F2": "Apple",
            "00:1E:C2": "Apple",
            "00:21:E9": "Apple",
            "00:22:41": "Apple",
            "00:23:12": "Apple",
            "00:23:32": "Apple",
            "00:23:6C": "Apple",
            "00:24:36": "Apple",
            "00:25:00": "Apple",
            "00:25:BC": "Apple",
            "00:26:08": "Apple",
            "00:26:4A": "Apple",
            "00:26:B0": "Apple",
            "00:26:BB": "Apple",
            "00:50:56": "VMware",
            "00:0C:29": "VMware",
            "00:1C:14": "VMware",
            "00:50:C2": "VMware",
            "00:11:32": "Synology",
            "00:1E:68": "Quanta",
            "00:0F:FF": "Control4",
            "00:17:88": "Philips Hue",
            "00:17:C4": "Netgear",
            "00:1B:2F": "Netgear",
            "00:1E:2A": "Netgear",
            "00:1F:33": "Netgear",
            "00:14:BF": "Linksys",
            "00:1A:70": "Cisco",
            "00:1B:0D": "Cisco",
            "00:1D:45": "Cisco",
            "B8:27:EB": "Raspberry Pi",
            "DC:A6:32": "Raspberry Pi",
            "E4:5F:01": "Raspberry Pi",
            "28:CD:C1": "Raspberry Pi",
            "D8:3A:DD": "Raspberry Pi",
            "60:03:08": "Apple",
            "94:E9:79": "Liteon (common in laptops)",
            "F4:5C:89": "Apple",
            "10:DD:B1": "Apple",
            "18:AF:61": "Apple",
            "3C:15:C2": "Apple",
            "64:A5:C3": "Apple",
            "6C:40:08": "Apple",
            "78:4F:43": "Apple",
            "7C:11:BE": "Apple",
            "98:01:A7": "Apple",
            "A4:5E:60": "Apple",
            "AC:BC:32": "Apple",
            "BC:52:B7": "Apple",
            "C8:2A:14": "Apple",
            "D0:4F:7E": "Apple",
            "D4:F4:6F": "Apple",
            "E0:B9:BA": "Apple",
            "E4:CE:8F": "Apple",
            "F0:B4:79": "Apple",
        }
        
        mac_upper = mac.upper()
        prefix = mac_upper[:8]
        
        return OUI_PREFIXES.get(prefix)
    
    def start_discovery(self, callback: Callable, duration: float = 10.0) -> bool:
        """Start network device discovery using all available methods."""
        if not self._is_available:
            self._report_error("WiFi discovery not available")
            return False
        
        if self._scan_active:
            print(f"[{self.name}] Scan already in progress.")
            return False
        
        self._scan_active = True
        self._discovered_ips.clear()
        self.state = AdapterState.SCANNING
        
        def scan_thread():
            try:
                # Start mDNS (runs continuously until stopped)
                if self._zeroconf_available:
                    self._start_mdns_discovery(callback)
                
                # Run SSDP discovery
                self._ssdp_discover(callback, timeout=min(duration, 5.0))
                
                # Run ARP scan if available
                if self._scapy_available:
                    self._arp_scan(callback, timeout=min(duration, 10.0))
                
                # Keep mDNS running for the remaining duration
                if self._zeroconf_available:
                    remaining = duration - 5.0
                    if remaining > 0:
                        time.sleep(remaining)
                
            except Exception as e:
                self._report_error(f"Discovery error: {e}")
            finally:
                self._stop_mdns_discovery()
                self._scan_active = False
                self.state = AdapterState.READY
        
        self._scan_thread = threading.Thread(target=scan_thread, daemon=True)
        self._scan_thread.start()
        
        return True
    
    def stop_discovery(self):
        """Stop all network discovery."""
        self._scan_active = False
        self._stop_mdns_discovery()
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2.0)
        self.state = AdapterState.READY
        print(f"[{self.name}] Discovery stopped.")
    
    def connect(self, device_id: str) -> bool:
        """Connect to a network device (establish TCP connection to service)."""
        # For WiFi devices, "connecting" means verifying reachability
        # Actual service connections are protocol-specific
        print(f"[{self.name}] WiFi devices are network-reachable by default")
        return True
    
    def disconnect(self, device_id: str) -> bool:
        """Disconnect from a network device."""
        return True
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a network device (requires IP:port:data format)."""
        # This is a generic method - actual communication should use
        # protocol-specific methods (HTTP, MQTT, etc.)
        self._report_error("Use protocol-specific communication methods")
        return False
    
    def receive_data(self, device_id: str, timeout: float = 5.0) -> Optional[bytes]:
        """Receive data from a network device."""
        return None
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device info (attempt to fetch from device)."""
        # Would need to implement protocol-specific info fetching
        return None
    
    def ping_device(self, ip: str, timeout: float = 1.0) -> bool:
        """Check if a device is reachable."""
        try:
            import subprocess
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(int(timeout)), ip],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def shutdown(self):
        """Shutdown the WiFi adapter."""
        self.stop_discovery()
        super().shutdown()
