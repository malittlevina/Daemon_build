# devices/device_bridge.py
"""
Device Bridge
=============
Connects the device discovery system to the daemon and other subsystems.
Provides high-level device management APIs for AI agents.

This bridge enables:
- Automatic device discovery and integration
- Device capability mapping to system actions
- Event routing to scroll triggers
- Semantic device queries
"""

import threading
import time
import json
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, asdict

from .device_registry import (
    DeviceRegistry, Device, DeviceProtocol, DeviceState, DeviceCapability
)
from .discovery_engine import DeviceDiscoveryEngine, DiscoveryMode, DiscoveryConfig


@dataclass
class DeviceEvent:
    """Represents a device-related event for scroll triggers."""
    event_type: str  # discovered, connected, disconnected, data_received
    device_id: str
    device_name: str
    protocol: str
    timestamp: float
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class DeviceBridge:
    """
    High-level bridge between device discovery and the daemon.
    Designed for AI-native interaction and management.
    """
    
    def __init__(self, config_path: str = "config/device_config.json"):
        self.config_path = config_path
        self._engine: Optional[DeviceDiscoveryEngine] = None
        self._initialized = False
        
        # Event subscribers
        self._event_subscribers: List[Callable[[DeviceEvent], None]] = []
        
        # Capability handlers - maps capabilities to handler functions
        self._capability_handlers: Dict[DeviceCapability, List[Callable]] = {}
        
        # Device aliases for semantic access
        self._device_aliases: Dict[str, str] = {}  # alias -> device_id
        
        # Action queue for device operations
        self._action_queue: List[Dict[str, Any]] = []
        self._action_lock = threading.Lock()
        
        # Load saved configuration
        self._load_config()
        
        print("[DeviceBridge] Initialized.")
    
    def _load_config(self):
        """Load device bridge configuration."""
        import os
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self._device_aliases = data.get('aliases', {})
                    print(f"[DeviceBridge] Loaded {len(self._device_aliases)} device aliases.")
            except Exception as e:
                print(f"[DeviceBridge] Config load error: {e}")
    
    def _save_config(self):
        """Save device bridge configuration."""
        import os
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                data = {
                    'aliases': self._device_aliases,
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[DeviceBridge] Config save error: {e}")
    
    def initialize(self, config: Optional[DiscoveryConfig] = None) -> bool:
        """
        Initialize the device bridge and underlying discovery engine.
        
        Args:
            config: Optional discovery configuration.
            
        Returns:
            True if initialization successful.
        """
        if self._initialized:
            print("[DeviceBridge] Already initialized.")
            return True
        
        print("[DeviceBridge] Initializing device subsystem...")
        
        self._engine = DeviceDiscoveryEngine()
        
        if config:
            self._engine.config = config
        
        # Initialize adapters
        results = self._engine.initialize_adapters()
        
        # Register callbacks
        self._engine.register_discovery_callback(self._on_device_discovered)
        self._engine.register_connection_callback(self._on_connection_changed)
        
        # Also register with registry for detailed events
        self._engine.registry.register_callback('device_discovered', self._on_registry_event)
        self._engine.registry.register_callback('device_connected', self._on_registry_event)
        self._engine.registry.register_callback('device_disconnected', self._on_registry_event)
        
        self._initialized = True
        
        available = [k for k, v in results.items() if v]
        print(f"[DeviceBridge] Initialized with protocols: {available}")
        
        return True
    
    def _on_device_discovered(self, device: Device):
        """Handle device discovery."""
        event = DeviceEvent(
            event_type='discovered',
            device_id=device.id,
            device_name=device.name,
            protocol=device.protocol.value,
            timestamp=time.time(),
            data=device.metadata.custom_data
        )
        self._emit_event(event)
    
    def _on_connection_changed(self, device: Device, connected: bool):
        """Handle device connection/disconnection."""
        event_type = 'connected' if connected else 'disconnected'
        event = DeviceEvent(
            event_type=event_type,
            device_id=device.id,
            device_name=device.name,
            protocol=device.protocol.value,
            timestamp=time.time()
        )
        self._emit_event(event)
        
        # Trigger capability handlers if connected
        if connected:
            for capability in device.capabilities:
                handlers = self._capability_handlers.get(capability, [])
                for handler in handlers:
                    try:
                        handler(device)
                    except Exception as e:
                        print(f"[DeviceBridge] Handler error: {e}")
    
    def _on_registry_event(self, device: Device):
        """Handle registry events."""
        pass  # Already handled by discovery/connection callbacks
    
    def _emit_event(self, event: DeviceEvent):
        """Emit event to all subscribers."""
        for subscriber in self._event_subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"[DeviceBridge] Event subscriber error: {e}")
    
    def subscribe_events(self, callback: Callable[[DeviceEvent], None]):
        """Subscribe to device events."""
        self._event_subscribers.append(callback)
    
    def register_capability_handler(
        self,
        capability: DeviceCapability,
        handler: Callable[[Device], None]
    ):
        """Register a handler for when devices with a capability connect."""
        if capability not in self._capability_handlers:
            self._capability_handlers[capability] = []
        self._capability_handlers[capability].append(handler)
    
    # ==================
    # Discovery Commands
    # ==================
    
    def start_discovery(self, continuous: bool = False) -> bool:
        """Start device discovery."""
        if not self._initialized:
            print("[DeviceBridge] Not initialized. Call initialize() first.")
            return False
        
        mode = DiscoveryMode.CONTINUOUS if continuous else DiscoveryMode.ONCE
        return self._engine.start_discovery(mode)
    
    def stop_discovery(self):
        """Stop device discovery."""
        if self._engine:
            self._engine.stop_discovery()
    
    def scan_now(self, protocols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform an immediate scan and return results as dictionaries.
        
        Args:
            protocols: Optional list of protocols to scan ['bluetooth', 'wifi', 'nfc', 'usb']
            
        Returns:
            List of device dictionaries.
        """
        if not self._initialized:
            return []
        
        devices = self._engine.scan_now(protocols)
        return [d.to_dict() for d in devices]
    
    # =================
    # Device Management
    # =================
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all discovered devices as dictionaries."""
        if not self._engine:
            return []
        return [d.to_dict() for d in self._engine.get_all_devices()]
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """Get all connected devices."""
        if not self._engine:
            return []
        return [d.to_dict() for d in self._engine.get_connected_devices()]
    
    def get_device(self, device_id_or_alias: str) -> Optional[Dict[str, Any]]:
        """Get a device by ID or alias."""
        if not self._engine:
            return None
        
        # Check if it's an alias
        device_id = self._device_aliases.get(device_id_or_alias, device_id_or_alias)
        
        device = self._engine.registry.get_device(device_id)
        return device.to_dict() if device else None
    
    def connect(self, device_id_or_alias: str) -> bool:
        """Connect to a device."""
        if not self._engine:
            return False
        
        device_id = self._device_aliases.get(device_id_or_alias, device_id_or_alias)
        return self._engine.connect_device(device_id)
    
    def disconnect(self, device_id_or_alias: str) -> bool:
        """Disconnect from a device."""
        if not self._engine:
            return False
        
        device_id = self._device_aliases.get(device_id_or_alias, device_id_or_alias)
        return self._engine.disconnect_device(device_id)
    
    def trust(self, device_id_or_alias: str, auto_connect: bool = True):
        """Trust a device for auto-reconnection."""
        if not self._engine:
            return
        
        device_id = self._device_aliases.get(device_id_or_alias, device_id_or_alias)
        self._engine.trust_device(device_id, auto_connect)
    
    def forget(self, device_id_or_alias: str):
        """Forget a device."""
        if not self._engine:
            return
        
        device_id = self._device_aliases.get(device_id_or_alias, device_id_or_alias)
        
        # Remove alias if exists
        for alias, did in list(self._device_aliases.items()):
            if did == device_id:
                del self._device_aliases[alias]
        
        self._engine.forget_device(device_id)
        self._save_config()
    
    # ===============
    # Semantic Access
    # ===============
    
    def set_alias(self, device_id: str, alias: str):
        """Set a friendly alias for a device."""
        self._device_aliases[alias.lower()] = device_id
        self._save_config()
        print(f"[DeviceBridge] Alias set: '{alias}' -> {device_id}")
    
    def get_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """Get device by alias."""
        return self.get_device(alias.lower())
    
    def find_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Find devices matching a name pattern."""
        if not self._engine:
            return []
        devices = self._engine.find_devices_by_name(name_pattern)
        return [d.to_dict() for d in devices]
    
    def find_by_capability(self, capability: Union[str, DeviceCapability]) -> List[Dict[str, Any]]:
        """Find devices with a specific capability."""
        if not self._engine:
            return []
        
        if isinstance(capability, str):
            try:
                capability = DeviceCapability[capability.upper()]
            except KeyError:
                return []
        
        devices = self._engine.find_devices_by_capability(capability)
        return [d.to_dict() for d in devices]
    
    def find_speakers(self) -> List[Dict[str, Any]]:
        """Find all speaker devices."""
        return self.find_by_capability(DeviceCapability.SPEAKER)
    
    def find_cameras(self) -> List[Dict[str, Any]]:
        """Find all camera devices."""
        return self.find_by_capability(DeviceCapability.CAMERA)
    
    def find_sensors(self) -> List[Dict[str, Any]]:
        """Find all sensor devices."""
        sensors = []
        for cap in [
            DeviceCapability.SENSOR_TEMPERATURE,
            DeviceCapability.SENSOR_HUMIDITY,
            DeviceCapability.SENSOR_MOTION,
            DeviceCapability.SENSOR_LIGHT,
            DeviceCapability.SENSOR_PROXIMITY,
            DeviceCapability.SENSOR_ACCELEROMETER,
        ]:
            sensors.extend(self.find_by_capability(cap))
        # Remove duplicates
        seen = set()
        unique = []
        for s in sensors:
            if s['id'] not in seen:
                seen.add(s['id'])
                unique.append(s)
        return unique
    
    def find_storage(self) -> List[Dict[str, Any]]:
        """Find all storage devices."""
        return self.find_by_capability(DeviceCapability.STORAGE)
    
    # =============
    # AI Interface
    # =============
    
    def query(self, natural_language: str) -> Dict[str, Any]:
        """
        Query devices using natural language.
        
        Examples:
            "find all bluetooth devices"
            "show connected devices"
            "find speakers"
            "what devices are nearby"
            
        Returns dict with 'devices' and 'message' keys.
        """
        query_lower = natural_language.lower()
        
        result = {
            'query': natural_language,
            'devices': [],
            'message': ''
        }
        
        # Parse query
        if 'bluetooth' in query_lower:
            devices = [d for d in self.get_all_devices() 
                      if d['protocol'] in ('bluetooth', 'bluetooth_le')]
            result['message'] = f"Found {len(devices)} Bluetooth device(s)"
            
        elif 'wifi' in query_lower or 'network' in query_lower:
            devices = [d for d in self.get_all_devices() if d['protocol'] == 'wifi']
            result['message'] = f"Found {len(devices)} WiFi device(s)"
            
        elif 'usb' in query_lower:
            devices = [d for d in self.get_all_devices() if d['protocol'] == 'usb']
            result['message'] = f"Found {len(devices)} USB device(s)"
            
        elif 'nfc' in query_lower or 'tag' in query_lower:
            devices = [d for d in self.get_all_devices() if d['protocol'] == 'nfc']
            result['message'] = f"Found {len(devices)} NFC device(s)"
            
        elif 'connected' in query_lower:
            devices = self.get_connected_devices()
            result['message'] = f"{len(devices)} device(s) connected"
            
        elif 'speaker' in query_lower or 'audio' in query_lower:
            devices = self.find_speakers()
            result['message'] = f"Found {len(devices)} speaker(s)"
            
        elif 'camera' in query_lower:
            devices = self.find_cameras()
            result['message'] = f"Found {len(devices)} camera(s)"
            
        elif 'sensor' in query_lower:
            devices = self.find_sensors()
            result['message'] = f"Found {len(devices)} sensor(s)"
            
        elif 'storage' in query_lower or 'drive' in query_lower:
            devices = self.find_storage()
            result['message'] = f"Found {len(devices)} storage device(s)"
            
        elif 'all' in query_lower or 'nearby' in query_lower or 'find' in query_lower:
            devices = self.get_all_devices()
            result['message'] = f"Found {len(devices)} device(s) total"
            
        else:
            # Try name search
            words = query_lower.split()
            for word in words:
                if len(word) > 2:
                    devices = self.find_by_name(word)
                    if devices:
                        result['message'] = f"Found {len(devices)} device(s) matching '{word}'"
                        break
            else:
                devices = self.get_all_devices()
                result['message'] = f"Showing all {len(devices)} device(s)"
        
        result['devices'] = devices
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge and engine status."""
        status = {
            'initialized': self._initialized,
            'event_subscribers': len(self._event_subscribers),
            'aliases': len(self._device_aliases),
        }
        
        if self._engine:
            status['engine'] = self._engine.get_status()
        
        return status
    
    def shutdown(self):
        """Shutdown the device bridge."""
        print("[DeviceBridge] Shutting down...")
        
        if self._engine:
            self._engine.shutdown()
        
        self._save_config()
        self._initialized = False
        
        print("[DeviceBridge] Shutdown complete.")


# Global bridge instance for daemon integration
_global_bridge: Optional[DeviceBridge] = None


def get_device_bridge() -> DeviceBridge:
    """Get or create the global device bridge instance."""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = DeviceBridge()
    return _global_bridge


def init_device_bridge(config: Optional[DiscoveryConfig] = None) -> DeviceBridge:
    """Initialize and return the global device bridge."""
    bridge = get_device_bridge()
    bridge.initialize(config)
    return bridge
