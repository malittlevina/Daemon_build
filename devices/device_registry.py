# devices/device_registry.py
"""
Unified Device Registry
=======================
Central registry for all discovered and connected devices.
Provides a unified interface regardless of underlying protocol.
"""

import json
import os
import time
import threading
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime


class DeviceProtocol(Enum):
    """Supported device connection protocols."""
    BLUETOOTH = "bluetooth"
    BLUETOOTH_LE = "bluetooth_le"
    WIFI = "wifi"
    NFC = "nfc"
    USB = "usb"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    MATTER = "matter"
    THREAD = "thread"
    UNKNOWN = "unknown"


class DeviceState(Enum):
    """Device connection states."""
    DISCOVERED = "discovered"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PAIRED = "paired"
    AUTHENTICATED = "authenticated"
    DISCONNECTED = "disconnected"
    UNREACHABLE = "unreachable"
    ERROR = "error"


class DeviceCapability(Enum):
    """Device capabilities for smart integration."""
    # Input capabilities
    SENSOR_TEMPERATURE = auto()
    SENSOR_HUMIDITY = auto()
    SENSOR_MOTION = auto()
    SENSOR_LIGHT = auto()
    SENSOR_PRESSURE = auto()
    SENSOR_PROXIMITY = auto()
    SENSOR_ACCELEROMETER = auto()
    SENSOR_GYROSCOPE = auto()
    CAMERA = auto()
    MICROPHONE = auto()
    GPS = auto()
    
    # Output capabilities
    DISPLAY = auto()
    SPEAKER = auto()
    LED = auto()
    MOTOR = auto()
    RELAY = auto()
    
    # Control capabilities
    SWITCH = auto()
    DIMMER = auto()
    THERMOSTAT = auto()
    LOCK = auto()
    
    # Data capabilities
    STORAGE = auto()
    COMPUTE = auto()
    NETWORK_BRIDGE = auto()
    
    # Communication
    VOICE_ASSISTANT = auto()
    NOTIFICATION = auto()
    MEDIA_PLAYBACK = auto()
    FILE_TRANSFER = auto()


@dataclass
class DeviceMetadata:
    """Extended device metadata for AI-driven management."""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    serial_number: Optional[str] = None
    hardware_revision: Optional[str] = None
    software_version: Optional[str] = None
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None  # RSSI for wireless
    last_seen: Optional[float] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Device:
    """
    Unified device representation.
    Works across all protocols with protocol-specific extensions.
    """
    id: str  # Unique identifier (MAC, UUID, etc.)
    name: str
    protocol: DeviceProtocol
    state: DeviceState = DeviceState.DISCOVERED
    address: Optional[str] = None  # Protocol-specific address
    capabilities: List[DeviceCapability] = field(default_factory=list)
    metadata: DeviceMetadata = field(default_factory=DeviceMetadata)
    services: Dict[str, Any] = field(default_factory=dict)  # Protocol-specific services
    is_trusted: bool = False
    auto_connect: bool = False
    discovered_at: float = field(default_factory=time.time)
    last_connected: Optional[float] = None
    connection_attempts: int = 0
    
    def to_dict(self) -> dict:
        """Serialize device to dictionary for storage/transmission."""
        data = asdict(self)
        data['protocol'] = self.protocol.value
        data['state'] = self.state.value
        data['capabilities'] = [c.name for c in self.capabilities]
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Device':
        """Deserialize device from dictionary."""
        data['protocol'] = DeviceProtocol(data['protocol'])
        data['state'] = DeviceState(data['state'])
        data['capabilities'] = [DeviceCapability[c] for c in data.get('capabilities', [])]
        data['metadata'] = DeviceMetadata(**data.get('metadata', {}))
        return cls(**data)
    
    def update_signal(self, rssi: int):
        """Update signal strength reading."""
        self.metadata.signal_strength = rssi
        self.metadata.last_seen = time.time()
    
    def mark_connected(self):
        """Mark device as connected."""
        self.state = DeviceState.CONNECTED
        self.last_connected = time.time()
        self.connection_attempts = 0
    
    def mark_disconnected(self):
        """Mark device as disconnected."""
        self.state = DeviceState.DISCONNECTED
    
    def __str__(self):
        return f"Device({self.name}, {self.protocol.value}, {self.state.value})"


class DeviceRegistry:
    """
    Central registry for all devices.
    Provides thread-safe access and persistence.
    """
    
    def __init__(self, persist_path: str = "config/device_registry.json"):
        self.persist_path = persist_path
        self._devices: Dict[str, Device] = {}
        self._lock = threading.RLock()
        self._callbacks: Dict[str, List[Callable]] = {
            'device_discovered': [],
            'device_connected': [],
            'device_disconnected': [],
            'device_updated': [],
            'device_removed': []
        }
        self._load_registry()
        print("[DeviceRegistry] Initialized with", len(self._devices), "persisted devices.")
    
    def _load_registry(self):
        """Load persisted device registry."""
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r') as f:
                    data = json.load(f)
                    for device_data in data.get('devices', []):
                        try:
                            device = Device.from_dict(device_data)
                            # Reset state on load - device needs rediscovery
                            device.state = DeviceState.DISCONNECTED
                            self._devices[device.id] = device
                        except Exception as e:
                            print(f"[DeviceRegistry] Failed to load device: {e}")
            except Exception as e:
                print(f"[DeviceRegistry] Failed to load registry: {e}")
    
    def _save_registry(self):
        """Persist device registry to disk."""
        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            with open(self.persist_path, 'w') as f:
                data = {
                    'version': 1,
                    'updated_at': datetime.now().isoformat(),
                    'devices': [d.to_dict() for d in self._devices.values() if d.is_trusted]
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[DeviceRegistry] Failed to save registry: {e}")
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for device events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, device: Device):
        """Emit an event to all registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(device)
            except Exception as e:
                print(f"[DeviceRegistry] Callback error for {event}: {e}")
    
    def add_device(self, device: Device) -> bool:
        """Add or update a device in the registry."""
        with self._lock:
            is_new = device.id not in self._devices
            self._devices[device.id] = device
            
            if is_new:
                print(f"[DeviceRegistry] New device discovered: {device}")
                self._emit('device_discovered', device)
            else:
                self._emit('device_updated', device)
            
            if device.is_trusted:
                self._save_registry()
            
            return is_new
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get a device by ID."""
        with self._lock:
            return self._devices.get(device_id)
    
    def get_all_devices(self) -> List[Device]:
        """Get all registered devices."""
        with self._lock:
            return list(self._devices.values())
    
    def get_devices_by_protocol(self, protocol: DeviceProtocol) -> List[Device]:
        """Get all devices using a specific protocol."""
        with self._lock:
            return [d for d in self._devices.values() if d.protocol == protocol]
    
    def get_devices_by_state(self, state: DeviceState) -> List[Device]:
        """Get all devices in a specific state."""
        with self._lock:
            return [d for d in self._devices.values() if d.state == state]
    
    def get_devices_by_capability(self, capability: DeviceCapability) -> List[Device]:
        """Get all devices with a specific capability."""
        with self._lock:
            return [d for d in self._devices.values() if capability in d.capabilities]
    
    def get_connected_devices(self) -> List[Device]:
        """Get all currently connected devices."""
        return self.get_devices_by_state(DeviceState.CONNECTED)
    
    def update_device_state(self, device_id: str, state: DeviceState):
        """Update a device's connection state."""
        with self._lock:
            device = self._devices.get(device_id)
            if device:
                old_state = device.state
                device.state = state
                
                if state == DeviceState.CONNECTED and old_state != DeviceState.CONNECTED:
                    device.last_connected = time.time()
                    self._emit('device_connected', device)
                elif state == DeviceState.DISCONNECTED and old_state == DeviceState.CONNECTED:
                    self._emit('device_disconnected', device)
                
                self._emit('device_updated', device)
    
    def trust_device(self, device_id: str, auto_connect: bool = True):
        """Mark a device as trusted for auto-reconnection."""
        with self._lock:
            device = self._devices.get(device_id)
            if device:
                device.is_trusted = True
                device.auto_connect = auto_connect
                self._save_registry()
                print(f"[DeviceRegistry] Device trusted: {device.name}")
    
    def remove_device(self, device_id: str):
        """Remove a device from the registry."""
        with self._lock:
            device = self._devices.pop(device_id, None)
            if device:
                self._emit('device_removed', device)
                self._save_registry()
                print(f"[DeviceRegistry] Device removed: {device.name}")
    
    def cleanup_stale_devices(self, max_age_seconds: float = 3600):
        """Remove devices that haven't been seen recently."""
        current_time = time.time()
        stale_ids = []
        
        with self._lock:
            for device_id, device in self._devices.items():
                if not device.is_trusted:
                    last_seen = device.metadata.last_seen or device.discovered_at
                    if current_time - last_seen > max_age_seconds:
                        stale_ids.append(device_id)
        
        for device_id in stale_ids:
            self.remove_device(device_id)
        
        if stale_ids:
            print(f"[DeviceRegistry] Cleaned up {len(stale_ids)} stale devices.")
    
    def get_summary(self) -> dict:
        """Get a summary of the device registry state."""
        with self._lock:
            return {
                'total_devices': len(self._devices),
                'connected': len(self.get_devices_by_state(DeviceState.CONNECTED)),
                'trusted': len([d for d in self._devices.values() if d.is_trusted]),
                'by_protocol': {
                    p.value: len(self.get_devices_by_protocol(p))
                    for p in DeviceProtocol
                    if self.get_devices_by_protocol(p)
                }
            }
