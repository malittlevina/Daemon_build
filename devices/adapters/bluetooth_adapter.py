# devices/adapters/bluetooth_adapter.py
"""
Bluetooth & BLE Adapter
=======================
Handles Bluetooth Classic and Bluetooth Low Energy device discovery,
connection, and communication.

Dependencies:
- bleak: For BLE operations (cross-platform)
- pybluez: For Bluetooth Classic (optional, Linux)
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from .base_adapter import BaseProtocolAdapter, AdapterState

# Import device registry types
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from devices.device_registry import (
    Device, DeviceProtocol, DeviceState, DeviceCapability, DeviceMetadata
)


class BluetoothAdapter(BaseProtocolAdapter):
    """
    Bluetooth and BLE adapter using bleak library.
    Provides unified scanning for both BLE and Classic devices.
    """
    
    # Known BLE service UUIDs for capability detection
    KNOWN_SERVICES = {
        "0000180d-0000-1000-8000-00805f9b34fb": DeviceCapability.SENSOR_ACCELEROMETER,  # Heart Rate
        "0000180a-0000-1000-8000-00805f9b34fb": None,  # Device Information
        "0000180f-0000-1000-8000-00805f9b34fb": None,  # Battery Service
        "00001800-0000-1000-8000-00805f9b34fb": None,  # Generic Access
        "00001801-0000-1000-8000-00805f9b34fb": None,  # Generic Attribute
        "0000181a-0000-1000-8000-00805f9b34fb": DeviceCapability.SENSOR_TEMPERATURE,  # Environmental Sensing
        "00001802-0000-1000-8000-00805f9b34fb": DeviceCapability.NOTIFICATION,  # Immediate Alert
        "00001803-0000-1000-8000-00805f9b34fb": DeviceCapability.NOTIFICATION,  # Link Loss
        "00001804-0000-1000-8000-00805f9b34fb": DeviceCapability.SENSOR_PROXIMITY,  # Tx Power
        "0000110b-0000-1000-8000-00805f9b34fb": DeviceCapability.SPEAKER,  # A2DP Audio Sink
        "0000110a-0000-1000-8000-00805f9b34fb": DeviceCapability.MEDIA_PLAYBACK,  # A2DP Source
        "0000111e-0000-1000-8000-00805f9b34fb": DeviceCapability.VOICE_ASSISTANT,  # Handsfree
    }
    
    def __init__(self):
        super().__init__("BluetoothAdapter")
        self._bleak_available = False
        self._pybluez_available = False
        self._connected_devices: Dict[str, Any] = {}
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._scan_active = False
        
    def initialize(self) -> bool:
        """Initialize Bluetooth adapter and check for BLE support."""
        self.state = AdapterState.INITIALIZING
        print(f"[{self.name}] Initializing...")
        
        # Try to import bleak for BLE
        try:
            import bleak
            self._bleak_available = True
            print(f"[{self.name}] BLE support available (bleak {bleak.__version__})")
        except ImportError:
            print(f"[{self.name}] bleak not installed. BLE scanning unavailable.")
            print(f"[{self.name}] Install with: pip install bleak")
        
        # Try to import pybluez for Classic Bluetooth (optional)
        try:
            import bluetooth
            self._pybluez_available = True
            print(f"[{self.name}] Bluetooth Classic support available (pybluez)")
        except ImportError:
            print(f"[{self.name}] pybluez not installed. Classic Bluetooth limited.")
        
        self._is_available = self._bleak_available or self._pybluez_available
        
        if self._is_available:
            self.state = AdapterState.READY
            print(f"[{self.name}] Initialized successfully.")
        else:
            self.state = AdapterState.ERROR
            self._report_error("No Bluetooth libraries available")
            
        return self._is_available
    
    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create an event loop for async operations."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Loop is closed")
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    async def _ble_scan(self, callback: Callable, duration: float):
        """Async BLE scanning using bleak."""
        try:
            from bleak import BleakScanner
            
            print(f"[{self.name}] Starting BLE scan for {duration}s...")
            
            def detection_callback(ble_device, advertisement_data):
                if not self._scan_active:
                    return
                    
                # Create Device from BLE discovery
                device = self._ble_device_to_device(ble_device, advertisement_data)
                callback(device)
            
            scanner = BleakScanner(detection_callback=detection_callback)
            await scanner.start()
            
            # Scan for specified duration
            scan_start = time.time()
            while self._scan_active and (time.time() - scan_start) < duration:
                await asyncio.sleep(0.5)
            
            await scanner.stop()
            print(f"[{self.name}] BLE scan complete.")
            
        except Exception as e:
            self._report_error(f"BLE scan failed: {e}")
    
    def _ble_device_to_device(self, ble_device, advertisement_data) -> Device:
        """Convert bleak BLEDevice to our Device model."""
        # Determine capabilities from advertised services
        capabilities = []
        services = {}
        
        if advertisement_data.service_uuids:
            for uuid in advertisement_data.service_uuids:
                uuid_lower = uuid.lower()
                services[uuid_lower] = {'uuid': uuid}
                if uuid_lower in self.KNOWN_SERVICES:
                    cap = self.KNOWN_SERVICES[uuid_lower]
                    if cap and cap not in capabilities:
                        capabilities.append(cap)
        
        # Extract manufacturer data
        manufacturer_data = {}
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                manufacturer_data[company_id] = data.hex()
        
        metadata = DeviceMetadata(
            manufacturer=self._lookup_manufacturer(manufacturer_data),
            signal_strength=advertisement_data.rssi if hasattr(advertisement_data, 'rssi') else None,
            last_seen=time.time(),
            custom_data={
                'local_name': advertisement_data.local_name,
                'manufacturer_data': manufacturer_data,
                'service_data': {k: v.hex() for k, v in (advertisement_data.service_data or {}).items()},
                'tx_power': advertisement_data.tx_power
            }
        )
        
        return Device(
            id=ble_device.address,
            name=ble_device.name or advertisement_data.local_name or f"BLE Device {ble_device.address[-5:]}",
            protocol=DeviceProtocol.BLUETOOTH_LE,
            state=DeviceState.DISCOVERED,
            address=ble_device.address,
            capabilities=capabilities,
            metadata=metadata,
            services=services
        )
    
    def _lookup_manufacturer(self, manufacturer_data: Dict) -> Optional[str]:
        """Lookup manufacturer from company ID."""
        # Common Bluetooth company IDs
        COMPANY_IDS = {
            0x004C: "Apple",
            0x0006: "Microsoft",
            0x000F: "Broadcom",
            0x0075: "Samsung",
            0x00E0: "Google",
            0x0310: "Xiaomi",
            0x0157: "Huawei",
            0x0059: "Nordic Semiconductor",
            0x000D: "Texas Instruments",
            0x0131: "Tile",
            0x0822: "Govee",
            0x0969: "Philips Hue",
        }
        
        for company_id in manufacturer_data.keys():
            if company_id in COMPANY_IDS:
                return COMPANY_IDS[company_id]
        return None
    
    def _classic_scan(self, callback: Callable, duration: float):
        """Scan for Classic Bluetooth devices using pybluez."""
        try:
            import bluetooth
            
            print(f"[{self.name}] Starting Classic Bluetooth scan...")
            
            nearby_devices = bluetooth.discover_devices(
                duration=int(duration),
                lookup_names=True,
                lookup_class=True,
                flush_cache=True
            )
            
            for addr, name, device_class in nearby_devices:
                if not self._scan_active:
                    break
                    
                device = Device(
                    id=addr,
                    name=name or f"BT Device {addr[-5:]}",
                    protocol=DeviceProtocol.BLUETOOTH,
                    state=DeviceState.DISCOVERED,
                    address=addr,
                    capabilities=self._class_to_capabilities(device_class),
                    metadata=DeviceMetadata(
                        last_seen=time.time(),
                        custom_data={'device_class': device_class}
                    )
                )
                callback(device)
            
            print(f"[{self.name}] Classic scan complete. Found {len(nearby_devices)} devices.")
            
        except Exception as e:
            self._report_error(f"Classic BT scan failed: {e}")
    
    def _class_to_capabilities(self, device_class: int) -> List[DeviceCapability]:
        """Convert Bluetooth device class to capabilities."""
        capabilities = []
        
        # Major device class (bits 8-12)
        major_class = (device_class >> 8) & 0x1F
        
        if major_class == 0x01:  # Computer
            capabilities.extend([DeviceCapability.COMPUTE, DeviceCapability.FILE_TRANSFER])
        elif major_class == 0x02:  # Phone
            capabilities.extend([DeviceCapability.NOTIFICATION, DeviceCapability.FILE_TRANSFER])
        elif major_class == 0x03:  # LAN/Network
            capabilities.append(DeviceCapability.NETWORK_BRIDGE)
        elif major_class == 0x04:  # Audio/Video
            capabilities.extend([DeviceCapability.SPEAKER, DeviceCapability.MEDIA_PLAYBACK])
        elif major_class == 0x05:  # Peripheral
            pass  # Input devices
        elif major_class == 0x06:  # Imaging
            capabilities.append(DeviceCapability.CAMERA)
        elif major_class == 0x07:  # Wearable
            capabilities.extend([DeviceCapability.NOTIFICATION, DeviceCapability.SENSOR_ACCELEROMETER])
            
        return capabilities
    
    def start_discovery(self, callback: Callable, duration: float = 10.0) -> bool:
        """Start Bluetooth device discovery."""
        if not self._is_available:
            self._report_error("Bluetooth not available")
            return False
        
        if self._scan_active:
            print(f"[{self.name}] Scan already in progress.")
            return False
        
        self._scan_active = True
        self._scan_callback = callback
        self.state = AdapterState.SCANNING
        
        def scan_thread():
            if self._bleak_available:
                # Run BLE scan
                loop = self._get_event_loop()
                try:
                    loop.run_until_complete(self._ble_scan(callback, duration))
                except Exception as e:
                    self._report_error(f"BLE scan error: {e}")
            
            if self._pybluez_available and self._scan_active:
                # Also run classic scan
                self._classic_scan(callback, duration)
            
            self._scan_active = False
            self.state = AdapterState.READY
        
        self._scan_thread = threading.Thread(target=scan_thread, daemon=True)
        self._scan_thread.start()
        
        return True
    
    def stop_discovery(self):
        """Stop Bluetooth scanning."""
        self._scan_active = False
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2.0)
        self.state = AdapterState.READY
        print(f"[{self.name}] Discovery stopped.")
    
    async def _ble_connect(self, device_id: str) -> bool:
        """Connect to a BLE device."""
        try:
            from bleak import BleakClient
            
            client = BleakClient(device_id)
            await client.connect()
            
            if client.is_connected:
                self._connected_devices[device_id] = {
                    'client': client,
                    'connected_at': time.time()
                }
                
                # Discover services
                services = await client.get_services()
                print(f"[{self.name}] Connected to {device_id}")
                print(f"[{self.name}] Services: {[str(s.uuid) for s in services]}")
                
                return True
            return False
            
        except Exception as e:
            self._report_error(f"BLE connect failed: {e}")
            return False
    
    def connect(self, device_id: str) -> bool:
        """Connect to a Bluetooth device."""
        if not self._bleak_available:
            self._report_error("BLE not available for connections")
            return False
        
        self.state = AdapterState.CONNECTING
        
        loop = self._get_event_loop()
        try:
            result = loop.run_until_complete(self._ble_connect(device_id))
            self.state = AdapterState.READY
            return result
        except Exception as e:
            self._report_error(f"Connection failed: {e}")
            self.state = AdapterState.READY
            return False
    
    async def _ble_disconnect(self, device_id: str) -> bool:
        """Disconnect from a BLE device."""
        if device_id in self._connected_devices:
            try:
                client = self._connected_devices[device_id]['client']
                await client.disconnect()
                del self._connected_devices[device_id]
                print(f"[{self.name}] Disconnected from {device_id}")
                return True
            except Exception as e:
                self._report_error(f"Disconnect failed: {e}")
        return False
    
    def disconnect(self, device_id: str) -> bool:
        """Disconnect from a Bluetooth device."""
        if device_id not in self._connected_devices:
            return True
        
        loop = self._get_event_loop()
        return loop.run_until_complete(self._ble_disconnect(device_id))
    
    async def _ble_write(self, device_id: str, char_uuid: str, data: bytes) -> bool:
        """Write data to a BLE characteristic."""
        if device_id not in self._connected_devices:
            return False
        
        try:
            client = self._connected_devices[device_id]['client']
            await client.write_gatt_char(char_uuid, data)
            return True
        except Exception as e:
            self._report_error(f"Write failed: {e}")
            return False
    
    async def _ble_read(self, device_id: str, char_uuid: str) -> Optional[bytes]:
        """Read data from a BLE characteristic."""
        if device_id not in self._connected_devices:
            return None
        
        try:
            client = self._connected_devices[device_id]['client']
            data = await client.read_gatt_char(char_uuid)
            return bytes(data)
        except Exception as e:
            self._report_error(f"Read failed: {e}")
            return None
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a connected device (requires characteristic UUID in first 36 bytes)."""
        # For BLE, data should be prefixed with the characteristic UUID
        if len(data) < 36:
            self._report_error("Data must include characteristic UUID prefix")
            return False
        
        char_uuid = data[:36].decode('utf-8')
        actual_data = data[36:]
        
        loop = self._get_event_loop()
        return loop.run_until_complete(self._ble_write(device_id, char_uuid, actual_data))
    
    def receive_data(self, device_id: str, timeout: float = 5.0) -> Optional[bytes]:
        """Receive data from a device (not directly supported for BLE - use notifications)."""
        # BLE typically uses notifications, this is a simplified read
        self._report_error("Use characteristic-specific read methods for BLE")
        return None
    
    async def _get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device info from BLE device."""
        if device_id not in self._connected_devices:
            return None
        
        try:
            client = self._connected_devices[device_id]['client']
            services = await client.get_services()
            
            info = {
                'address': device_id,
                'connected': client.is_connected,
                'services': []
            }
            
            for service in services:
                svc_info = {
                    'uuid': str(service.uuid),
                    'characteristics': []
                }
                for char in service.characteristics:
                    svc_info['characteristics'].append({
                        'uuid': str(char.uuid),
                        'properties': char.properties
                    })
                info['services'].append(svc_info)
            
            return info
            
        except Exception as e:
            self._report_error(f"Get info failed: {e}")
            return None
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed device information."""
        loop = self._get_event_loop()
        return loop.run_until_complete(self._get_device_info(device_id))
    
    def get_connected_devices(self) -> List[str]:
        """Get list of connected device IDs."""
        return list(self._connected_devices.keys())
    
    def shutdown(self):
        """Shutdown the Bluetooth adapter."""
        self.stop_discovery()
        
        # Disconnect all devices
        loop = self._get_event_loop()
        for device_id in list(self._connected_devices.keys()):
            loop.run_until_complete(self._ble_disconnect(device_id))
        
        super().shutdown()
