# scrolls/device_scroll.py
"""
Device Scroll Triggers
======================
Scroll triggers and actions for device-related events.
Enables automation based on device discovery, connection, and data.
"""

from typing import Dict, Any, Optional, List, Callable


class DeviceScrollTrigger:
    """
    Scroll trigger that fires on device events.
    
    Trigger conditions:
    - device_discovered: When a new device is found
    - device_connected: When a device connects
    - device_disconnected: When a device disconnects
    - device_capability: When a device with specific capability is found
    - device_name_match: When a device matching a name pattern is found
    """
    
    def __init__(self):
        self.registered_triggers: List[Dict[str, Any]] = []
        self._event_handlers: Dict[str, List[Callable]] = {
            'device_discovered': [],
            'device_connected': [],
            'device_disconnected': [],
        }
    
    def on_discovered(
        self,
        handler: Callable,
        capability_filter: Optional[str] = None,
        protocol_filter: Optional[str] = None,
        name_pattern: Optional[str] = None
    ):
        """
        Register handler for device discovery events.
        
        Args:
            handler: Function(device_dict) to call
            capability_filter: Only trigger for devices with this capability
            protocol_filter: Only trigger for this protocol
            name_pattern: Only trigger if device name contains this pattern
        """
        self.registered_triggers.append({
            'event': 'device_discovered',
            'handler': handler,
            'filters': {
                'capability': capability_filter,
                'protocol': protocol_filter,
                'name_pattern': name_pattern
            }
        })
    
    def on_connected(
        self,
        handler: Callable,
        capability_filter: Optional[str] = None,
        protocol_filter: Optional[str] = None,
        name_pattern: Optional[str] = None
    ):
        """Register handler for device connection events."""
        self.registered_triggers.append({
            'event': 'device_connected',
            'handler': handler,
            'filters': {
                'capability': capability_filter,
                'protocol': protocol_filter,
                'name_pattern': name_pattern
            }
        })
    
    def on_disconnected(
        self,
        handler: Callable,
        capability_filter: Optional[str] = None,
        protocol_filter: Optional[str] = None,
        name_pattern: Optional[str] = None
    ):
        """Register handler for device disconnection events."""
        self.registered_triggers.append({
            'event': 'device_disconnected',
            'handler': handler,
            'filters': {
                'capability': capability_filter,
                'protocol': protocol_filter,
                'name_pattern': name_pattern
            }
        })
    
    def _matches_filters(self, device: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if a device matches the specified filters."""
        if filters.get('capability'):
            capabilities = device.get('capabilities', [])
            if filters['capability'].upper() not in [c.upper() if isinstance(c, str) else c for c in capabilities]:
                return False
        
        if filters.get('protocol'):
            if device.get('protocol', '').lower() != filters['protocol'].lower():
                return False
        
        if filters.get('name_pattern'):
            if filters['name_pattern'].lower() not in device.get('name', '').lower():
                return False
        
        return True
    
    def handle_event(self, event_type: str, device: Dict[str, Any]):
        """Process an event and call matching handlers."""
        for trigger in self.registered_triggers:
            if trigger['event'] == event_type:
                if self._matches_filters(device, trigger['filters']):
                    try:
                        trigger['handler'](device)
                    except Exception as e:
                        print(f"[DeviceScrollTrigger] Handler error: {e}")


class DeviceScrollAction:
    """
    Scroll actions for device operations.
    Can be used in scroll definitions to interact with devices.
    """
    
    def __init__(self, device_bridge):
        """
        Initialize with device bridge reference.
        
        Args:
            device_bridge: The DeviceBridge instance
        """
        self.bridge = device_bridge
    
    def scan_devices(self, protocols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scroll action to trigger device scan."""
        devices = self.bridge.scan_now(protocols)
        return {
            'action': 'scan_devices',
            'result': 'success',
            'device_count': len(devices),
            'devices': devices
        }
    
    def connect_device(self, device_id_or_alias: str) -> Dict[str, Any]:
        """Scroll action to connect to a device."""
        success = self.bridge.connect(device_id_or_alias)
        return {
            'action': 'connect_device',
            'target': device_id_or_alias,
            'result': 'success' if success else 'failed'
        }
    
    def disconnect_device(self, device_id_or_alias: str) -> Dict[str, Any]:
        """Scroll action to disconnect from a device."""
        success = self.bridge.disconnect(device_id_or_alias)
        return {
            'action': 'disconnect_device',
            'target': device_id_or_alias,
            'result': 'success' if success else 'failed'
        }
    
    def find_devices(self, query: str) -> Dict[str, Any]:
        """Scroll action to query devices."""
        result = self.bridge.query(query)
        return {
            'action': 'find_devices',
            'query': query,
            'result': 'success',
            'data': result
        }
    
    def set_device_alias(self, device_id: str, alias: str) -> Dict[str, Any]:
        """Scroll action to set device alias."""
        self.bridge.set_alias(device_id, alias)
        return {
            'action': 'set_device_alias',
            'device_id': device_id,
            'alias': alias,
            'result': 'success'
        }
    
    def trust_device(self, device_id_or_alias: str, auto_connect: bool = True) -> Dict[str, Any]:
        """Scroll action to trust a device."""
        self.bridge.trust(device_id_or_alias, auto_connect)
        return {
            'action': 'trust_device',
            'target': device_id_or_alias,
            'auto_connect': auto_connect,
            'result': 'success'
        }
    
    def get_device_status(self) -> Dict[str, Any]:
        """Scroll action to get device subsystem status."""
        status = self.bridge.get_status()
        return {
            'action': 'get_device_status',
            'result': 'success',
            'status': status
        }


# Example scroll definitions for device automation
DEVICE_SCROLL_EXAMPLES = """
# Device Scroll Examples
# ======================

# 1. Announce when a speaker connects
scroll "speaker_connected":
    trigger: device_connected
    filter:
        capability: SPEAKER
    action:
        - log: "Speaker connected: {{device.name}}"
        - notify: "Audio output available on {{device.name}}"

# 2. Auto-trust Raspberry Pi devices
scroll "trust_raspberry_pi":
    trigger: device_discovered
    filter:
        name_pattern: "Raspberry"
    action:
        - trust_device: "{{device.id}}"
        - log: "Trusted Raspberry Pi: {{device.name}}"

# 3. Scan for devices on wake
scroll "wake_device_scan":
    trigger: system_wake
    action:
        - scan_devices: ["bluetooth", "wifi"]
        - log: "Device scan completed"

# 4. Log all NFC tag reads
scroll "nfc_tag_log":
    trigger: device_discovered
    filter:
        protocol: "nfc"
    action:
        - log: "NFC tag detected: {{device.id}}"
        - memory_log: "NFC tag: {{device.metadata}}"
"""
