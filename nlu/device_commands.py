# nlu/device_commands.py
"""
Device Command Handler for NLU
==============================
Handles natural language commands related to device discovery,
connection, and management.
"""

import re
from typing import Optional, Dict, Any, Tuple


class DeviceCommandHandler:
    """
    Interprets natural language commands for device operations.
    Integrates with the NLU engine to handle device-related intents.
    """
    
    # Command patterns
    SCAN_PATTERNS = [
        r"scan\s*(for)?\s*devices?",
        r"find\s*(nearby)?\s*devices?",
        r"discover\s*devices?",
        r"search\s*(for)?\s*devices?",
        r"look\s*for\s*devices?",
        r"what\s*devices?\s*(are)?\s*(nearby|available|around)",
    ]
    
    CONNECT_PATTERNS = [
        r"connect\s*(to)?\s*(.+)",
        r"pair\s*(with)?\s*(.+)",
        r"link\s*(to)?\s*(.+)",
    ]
    
    DISCONNECT_PATTERNS = [
        r"disconnect\s*(from)?\s*(.+)",
        r"unpair\s*(from)?\s*(.+)",
        r"unlink\s*(from)?\s*(.+)",
    ]
    
    LIST_PATTERNS = [
        r"(list|show|display)\s*(all)?\s*(connected)?\s*devices?",
        r"what\s*(devices?)?\s*(is|are)\s*connected",
        r"connected\s*devices?",
    ]
    
    PROTOCOL_PATTERNS = [
        r"(scan|find|show)\s*(all)?\s*bluetooth\s*devices?",
        r"(scan|find|show)\s*(all)?\s*wifi\s*(devices?|networks?)?",
        r"(scan|find|show)\s*(all)?\s*usb\s*devices?",
        r"(scan|find|show)\s*(all)?\s*nfc\s*(devices?|tags?)?",
    ]
    
    CAPABILITY_PATTERNS = [
        r"(find|show|list)\s*(all)?\s*speakers?",
        r"(find|show|list)\s*(all)?\s*cameras?",
        r"(find|show|list)\s*(all)?\s*sensors?",
        r"(find|show|list)\s*(all)?\s*storage\s*(devices?)?",
        r"(find|show|list)\s*(all)?\s*displays?",
    ]
    
    STATUS_PATTERNS = [
        r"device\s*status",
        r"devices?\s*summary",
        r"how\s*many\s*devices?",
    ]
    
    TRUST_PATTERNS = [
        r"trust\s*(.+)",
        r"remember\s*(.+)",
        r"save\s*(.+)\s*device",
    ]
    
    FORGET_PATTERNS = [
        r"forget\s*(.+)",
        r"remove\s*(.+)\s*device",
        r"delete\s*(.+)",
    ]
    
    ALIAS_PATTERNS = [
        r"(call|name|alias)\s*(.+)\s*(as|to)\s*(.+)",
        r"set\s*alias\s*(.+)\s*(to|as|=)\s*(.+)",
    ]
    
    def __init__(self, device_bridge=None):
        """
        Initialize command handler.
        
        Args:
            device_bridge: Optional DeviceBridge instance.
                          If not provided, will be lazy-loaded.
        """
        self._bridge = device_bridge
    
    @property
    def bridge(self):
        """Lazy-load device bridge."""
        if self._bridge is None:
            try:
                from devices.device_bridge import get_device_bridge
                self._bridge = get_device_bridge()
                if not self._bridge._initialized:
                    self._bridge.initialize()
            except Exception as e:
                print(f"[DeviceCommandHandler] Bridge init error: {e}")
                return None
        return self._bridge
    
    def can_handle(self, text: str) -> bool:
        """Check if this handler can process the given text."""
        text_lower = text.lower()
        
        # Check for device-related keywords
        device_keywords = [
            'device', 'bluetooth', 'wifi', 'usb', 'nfc', 'tag',
            'scan', 'connect', 'disconnect', 'pair', 'unpair',
            'speaker', 'camera', 'sensor', 'storage'
        ]
        
        return any(keyword in text_lower for keyword in device_keywords)
    
    def handle(self, text: str) -> Optional[str]:
        """
        Handle a device-related command.
        
        Args:
            text: Natural language command.
            
        Returns:
            Response string, or None if not handled.
        """
        text_lower = text.lower().strip()
        
        if not self.bridge:
            return "[Device] Device subsystem not available."
        
        # Try each command type
        result = self._try_scan(text_lower)
        if result:
            return result
        
        result = self._try_protocol_scan(text_lower)
        if result:
            return result
        
        result = self._try_capability_search(text_lower)
        if result:
            return result
        
        result = self._try_connect(text_lower)
        if result:
            return result
        
        result = self._try_disconnect(text_lower)
        if result:
            return result
        
        result = self._try_list(text_lower)
        if result:
            return result
        
        result = self._try_status(text_lower)
        if result:
            return result
        
        result = self._try_trust(text_lower)
        if result:
            return result
        
        result = self._try_forget(text_lower)
        if result:
            return result
        
        result = self._try_alias(text_lower, text)
        if result:
            return result
        
        # Generic device query
        if self.can_handle(text):
            query_result = self.bridge.query(text)
            return self._format_query_result(query_result)
        
        return None
    
    def _try_scan(self, text: str) -> Optional[str]:
        """Try to match scan command."""
        for pattern in self.SCAN_PATTERNS:
            if re.search(pattern, text):
                devices = self.bridge.scan_now()
                return self._format_device_list(devices, "Scan complete")
        return None
    
    def _try_protocol_scan(self, text: str) -> Optional[str]:
        """Try to match protocol-specific scan."""
        protocols = []
        
        if 'bluetooth' in text:
            protocols.append('bluetooth')
        if 'wifi' in text or 'network' in text:
            protocols.append('wifi')
        if 'usb' in text:
            protocols.append('usb')
        if 'nfc' in text or 'tag' in text:
            protocols.append('nfc')
        
        if protocols and any(word in text for word in ['scan', 'find', 'show', 'search', 'discover']):
            devices = self.bridge.scan_now(protocols)
            protocol_str = ', '.join(protocols)
            return self._format_device_list(devices, f"Scanned {protocol_str}")
        
        return None
    
    def _try_capability_search(self, text: str) -> Optional[str]:
        """Try to match capability search."""
        if 'speaker' in text:
            devices = self.bridge.find_speakers()
            return self._format_device_list(devices, "Speakers found")
        elif 'camera' in text:
            devices = self.bridge.find_cameras()
            return self._format_device_list(devices, "Cameras found")
        elif 'sensor' in text:
            devices = self.bridge.find_sensors()
            return self._format_device_list(devices, "Sensors found")
        elif 'storage' in text or 'drive' in text:
            devices = self.bridge.find_storage()
            return self._format_device_list(devices, "Storage devices found")
        
        return None
    
    def _try_connect(self, text: str) -> Optional[str]:
        """Try to match connect command."""
        for pattern in self.CONNECT_PATTERNS:
            match = re.search(pattern, text)
            if match:
                target = match.group(2).strip() if match.lastindex >= 2 else None
                if target:
                    success = self.bridge.connect(target)
                    if success:
                        return f"[Device] Connected to: {target}"
                    else:
                        return f"[Device] Failed to connect to: {target}"
        return None
    
    def _try_disconnect(self, text: str) -> Optional[str]:
        """Try to match disconnect command."""
        for pattern in self.DISCONNECT_PATTERNS:
            match = re.search(pattern, text)
            if match:
                target = match.group(2).strip() if match.lastindex >= 2 else None
                if target:
                    success = self.bridge.disconnect(target)
                    if success:
                        return f"[Device] Disconnected from: {target}"
                    else:
                        return f"[Device] Failed to disconnect from: {target}"
        return None
    
    def _try_list(self, text: str) -> Optional[str]:
        """Try to match list command."""
        for pattern in self.LIST_PATTERNS:
            if re.search(pattern, text):
                if 'connected' in text:
                    devices = self.bridge.get_connected_devices()
                    return self._format_device_list(devices, "Connected devices")
                else:
                    devices = self.bridge.get_all_devices()
                    return self._format_device_list(devices, "All known devices")
        return None
    
    def _try_status(self, text: str) -> Optional[str]:
        """Try to match status command."""
        for pattern in self.STATUS_PATTERNS:
            if re.search(pattern, text):
                status = self.bridge.get_status()
                
                if 'engine' in status and status['engine']:
                    registry = status['engine'].get('registry', {})
                    total = registry.get('total_devices', 0)
                    connected = registry.get('connected', 0)
                    protocols = registry.get('by_protocol', {})
                    
                    lines = [
                        f"[Device Status]",
                        f"  Total devices: {total}",
                        f"  Connected: {connected}",
                    ]
                    if protocols:
                        lines.append("  By protocol:")
                        for proto, count in protocols.items():
                            lines.append(f"    - {proto}: {count}")
                    
                    return "\n".join(lines)
                
                return f"[Device Status] Initialized: {status.get('initialized', False)}"
        return None
    
    def _try_trust(self, text: str) -> Optional[str]:
        """Try to match trust command."""
        for pattern in self.TRUST_PATTERNS:
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                if target:
                    self.bridge.trust(target, auto_connect=True)
                    return f"[Device] Trusted: {target} (will auto-connect)"
        return None
    
    def _try_forget(self, text: str) -> Optional[str]:
        """Try to match forget command."""
        for pattern in self.FORGET_PATTERNS:
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                if target:
                    self.bridge.forget(target)
                    return f"[Device] Forgotten: {target}"
        return None
    
    def _try_alias(self, text_lower: str, original_text: str) -> Optional[str]:
        """Try to match alias command."""
        # Pattern: "call X as Y" or "name X to Y" or "alias X to Y"
        match = re.search(r"(?:call|name|alias)\s+(.+?)\s+(?:as|to)\s+(.+)", text_lower)
        if match:
            device_id = match.group(1).strip()
            alias = match.group(2).strip()
            self.bridge.set_alias(device_id, alias)
            return f"[Device] Alias set: '{alias}' -> {device_id}"
        
        return None
    
    def _format_device_list(self, devices: list, title: str) -> str:
        """Format a list of devices for display."""
        if not devices:
            return f"[{title}] No devices found."
        
        lines = [f"[{title}] {len(devices)} device(s):"]
        
        for i, device in enumerate(devices[:10], 1):  # Limit to 10
            name = device.get('name', 'Unknown')
            protocol = device.get('protocol', 'unknown')
            state = device.get('state', 'unknown')
            address = device.get('address', '')
            
            line = f"  {i}. {name} ({protocol})"
            if state == 'connected':
                line += " [Connected]"
            if address:
                line += f" - {address}"
            
            lines.append(line)
        
        if len(devices) > 10:
            lines.append(f"  ... and {len(devices) - 10} more")
        
        return "\n".join(lines)
    
    def _format_query_result(self, result: Dict[str, Any]) -> str:
        """Format a query result for display."""
        message = result.get('message', '')
        devices = result.get('devices', [])
        
        return self._format_device_list(devices, message)


# Singleton instance
_handler: Optional[DeviceCommandHandler] = None


def get_device_command_handler() -> DeviceCommandHandler:
    """Get the device command handler singleton."""
    global _handler
    if _handler is None:
        _handler = DeviceCommandHandler()
    return _handler


def handle_device_command(text: str) -> Optional[str]:
    """
    Convenience function to handle device commands.
    
    Args:
        text: Natural language command.
        
    Returns:
        Response string, or None if not a device command.
    """
    handler = get_device_command_handler()
    if handler.can_handle(text):
        return handler.handle(text)
    return None
