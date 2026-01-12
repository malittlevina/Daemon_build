# devices/discovery_engine.py
"""
Device Discovery Engine
=======================
Orchestrates all protocol adapters to provide unified, continuous
device discovery across Bluetooth, WiFi, NFC, USB, and more.

This is the central nervous system for device connectivity, designed
to be managed by AI agents for seamless device integration.
"""

import threading
import time
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum, auto
from dataclasses import dataclass, field

from .device_registry import (
    DeviceRegistry, Device, DeviceProtocol, DeviceState, DeviceCapability
)
from .adapters.base_adapter import BaseProtocolAdapter, AdapterState
from .adapters.bluetooth_adapter import BluetoothAdapter
from .adapters.wifi_adapter import WiFiAdapter
from .adapters.nfc_adapter import NFCAdapter
from .adapters.usb_adapter import USBAdapter


class DiscoveryMode(Enum):
    """Discovery operation modes."""
    IDLE = auto()           # Not scanning
    ONCE = auto()           # Single scan pass
    CONTINUOUS = auto()     # Continuous background scanning
    TARGETED = auto()       # Looking for specific device(s)


@dataclass
class DiscoveryConfig:
    """Configuration for device discovery."""
    # Enable/disable specific protocols
    bluetooth_enabled: bool = True
    wifi_enabled: bool = True
    nfc_enabled: bool = True
    usb_enabled: bool = True
    
    # Scan timing
    bluetooth_scan_duration: float = 10.0
    wifi_scan_duration: float = 15.0
    nfc_scan_duration: float = 30.0
    usb_scan_duration: float = 5.0
    
    # Continuous mode settings
    scan_interval: float = 60.0  # Seconds between scans in continuous mode
    stale_device_timeout: float = 300.0  # Seconds before marking device stale
    
    # Auto-connect settings
    auto_connect_trusted: bool = True
    
    # Filtering
    capability_filter: Optional[List[DeviceCapability]] = None
    protocol_filter: Optional[List[DeviceProtocol]] = None
    name_filter: Optional[str] = None


class DeviceDiscoveryEngine:
    """
    Central discovery engine that orchestrates all protocol adapters.
    Provides unified device discovery and management.
    """
    
    def __init__(self, registry: Optional[DeviceRegistry] = None):
        self.registry = registry or DeviceRegistry()
        self.config = DiscoveryConfig()
        self.mode = DiscoveryMode.IDLE
        
        # Initialize adapters
        self._adapters: Dict[str, BaseProtocolAdapter] = {}
        self._adapter_lock = threading.Lock()
        
        # Discovery state
        self._discovery_thread: Optional[threading.Thread] = None
        self._discovery_active = False
        self._last_scan_time: Dict[str, float] = {}
        self._seen_device_ids: Set[str] = set()
        
        # Callbacks
        self._discovery_callbacks: List[Callable[[Device], None]] = []
        self._connection_callbacks: List[Callable[[Device, bool], None]] = []
        
        print("[DiscoveryEngine] Initialized.")
    
    def initialize_adapters(self) -> Dict[str, bool]:
        """Initialize all protocol adapters and return their availability status."""
        print("[DiscoveryEngine] Initializing protocol adapters...")
        
        results = {}
        
        # Bluetooth
        if self.config.bluetooth_enabled:
            bt_adapter = BluetoothAdapter()
            results['bluetooth'] = bt_adapter.initialize()
            if results['bluetooth']:
                self._adapters['bluetooth'] = bt_adapter
        
        # WiFi
        if self.config.wifi_enabled:
            wifi_adapter = WiFiAdapter()
            results['wifi'] = wifi_adapter.initialize()
            if results['wifi']:
                self._adapters['wifi'] = wifi_adapter
        
        # NFC
        if self.config.nfc_enabled:
            nfc_adapter = NFCAdapter()
            results['nfc'] = nfc_adapter.initialize()
            if results['nfc']:
                self._adapters['nfc'] = nfc_adapter
        
        # USB
        if self.config.usb_enabled:
            usb_adapter = USBAdapter()
            results['usb'] = usb_adapter.initialize()
            if results['usb']:
                self._adapters['usb'] = usb_adapter
        
        print(f"[DiscoveryEngine] Adapters initialized: {results}")
        return results
    
    def register_discovery_callback(self, callback: Callable[[Device], None]):
        """Register a callback for when devices are discovered."""
        self._discovery_callbacks.append(callback)
    
    def register_connection_callback(self, callback: Callable[[Device, bool], None]):
        """Register a callback for device connection/disconnection events."""
        self._connection_callbacks.append(callback)
    
    def _on_device_discovered(self, device: Device):
        """Handle a newly discovered device."""
        # Apply filters
        if self.config.protocol_filter:
            if device.protocol not in self.config.protocol_filter:
                return
        
        if self.config.capability_filter:
            if not any(cap in device.capabilities for cap in self.config.capability_filter):
                return
        
        if self.config.name_filter:
            if self.config.name_filter.lower() not in device.name.lower():
                return
        
        # Update registry
        is_new = self.registry.add_device(device)
        
        # Track seen devices
        self._seen_device_ids.add(device.id)
        
        # Notify callbacks
        for callback in self._discovery_callbacks:
            try:
                callback(device)
            except Exception as e:
                print(f"[DiscoveryEngine] Callback error: {e}")
        
        # Auto-connect if trusted
        if self.config.auto_connect_trusted and device.is_trusted and device.auto_connect:
            self._auto_connect(device)
    
    def _auto_connect(self, device: Device):
        """Attempt to auto-connect to a trusted device."""
        adapter_name = self._get_adapter_for_protocol(device.protocol)
        if adapter_name and adapter_name in self._adapters:
            adapter = self._adapters[adapter_name]
            
            def connect_thread():
                try:
                    print(f"[DiscoveryEngine] Auto-connecting to {device.name}...")
                    success = adapter.connect(device.id)
                    if success:
                        device.mark_connected()
                        self.registry.update_device_state(device.id, DeviceState.CONNECTED)
                        for callback in self._connection_callbacks:
                            callback(device, True)
                except Exception as e:
                    print(f"[DiscoveryEngine] Auto-connect failed: {e}")
            
            threading.Thread(target=connect_thread, daemon=True).start()
    
    def _get_adapter_for_protocol(self, protocol: DeviceProtocol) -> Optional[str]:
        """Get the adapter name for a device protocol."""
        mapping = {
            DeviceProtocol.BLUETOOTH: 'bluetooth',
            DeviceProtocol.BLUETOOTH_LE: 'bluetooth',
            DeviceProtocol.WIFI: 'wifi',
            DeviceProtocol.NFC: 'nfc',
            DeviceProtocol.USB: 'usb',
        }
        return mapping.get(protocol)
    
    def start_discovery(self, mode: DiscoveryMode = DiscoveryMode.ONCE) -> bool:
        """Start device discovery in the specified mode."""
        if self._discovery_active:
            print("[DiscoveryEngine] Discovery already active.")
            return False
        
        if not self._adapters:
            print("[DiscoveryEngine] No adapters available. Call initialize_adapters() first.")
            return False
        
        self._discovery_active = True
        self.mode = mode
        self._seen_device_ids.clear()
        
        print(f"[DiscoveryEngine] Starting discovery in {mode.name} mode...")
        
        def discovery_loop():
            try:
                while self._discovery_active:
                    self._run_discovery_cycle()
                    
                    if self.mode == DiscoveryMode.ONCE:
                        break
                    elif self.mode == DiscoveryMode.CONTINUOUS:
                        # Wait for next scan interval
                        wait_time = 0
                        while wait_time < self.config.scan_interval and self._discovery_active:
                            time.sleep(1)
                            wait_time += 1
            except Exception as e:
                print(f"[DiscoveryEngine] Discovery error: {e}")
            finally:
                self._discovery_active = False
                self.mode = DiscoveryMode.IDLE
                print("[DiscoveryEngine] Discovery stopped.")
        
        self._discovery_thread = threading.Thread(target=discovery_loop, daemon=True)
        self._discovery_thread.start()
        
        return True
    
    def _run_discovery_cycle(self):
        """Run a single discovery cycle across all adapters."""
        print("[DiscoveryEngine] Running discovery cycle...")
        
        threads = []
        
        # Start discovery on each adapter
        with self._adapter_lock:
            for name, adapter in self._adapters.items():
                if adapter.state == AdapterState.READY:
                    duration = self._get_scan_duration(name)
                    
                    def start_adapter(n, a, d):
                        try:
                            a.start_discovery(self._on_device_discovered, d)
                            self._last_scan_time[n] = time.time()
                        except Exception as e:
                            print(f"[DiscoveryEngine] Adapter {n} error: {e}")
                    
                    t = threading.Thread(
                        target=start_adapter,
                        args=(name, adapter, duration),
                        daemon=True
                    )
                    threads.append(t)
                    t.start()
        
        # Wait for all scans to complete
        max_duration = max(
            self.config.bluetooth_scan_duration,
            self.config.wifi_scan_duration,
            self.config.nfc_scan_duration,
            self.config.usb_scan_duration
        )
        
        for t in threads:
            t.join(timeout=max_duration + 5)
        
        # Cleanup stale devices in continuous mode
        if self.mode == DiscoveryMode.CONTINUOUS:
            self.registry.cleanup_stale_devices(self.config.stale_device_timeout)
        
        print(f"[DiscoveryEngine] Discovery cycle complete. Found {len(self._seen_device_ids)} devices.")
    
    def _get_scan_duration(self, adapter_name: str) -> float:
        """Get the scan duration for an adapter."""
        durations = {
            'bluetooth': self.config.bluetooth_scan_duration,
            'wifi': self.config.wifi_scan_duration,
            'nfc': self.config.nfc_scan_duration,
            'usb': self.config.usb_scan_duration,
        }
        return durations.get(adapter_name, 10.0)
    
    def stop_discovery(self):
        """Stop all discovery operations."""
        print("[DiscoveryEngine] Stopping discovery...")
        self._discovery_active = False
        
        with self._adapter_lock:
            for adapter in self._adapters.values():
                adapter.stop_discovery()
        
        if self._discovery_thread and self._discovery_thread.is_alive():
            self._discovery_thread.join(timeout=5.0)
        
        self.mode = DiscoveryMode.IDLE
    
    def scan_now(self, protocols: Optional[List[str]] = None) -> List[Device]:
        """
        Perform an immediate scan and return discovered devices.
        Blocks until scan is complete.
        """
        discovered = []
        
        def collect_device(device: Device):
            discovered.append(device)
        
        self._discovery_callbacks.append(collect_device)
        
        try:
            # If specific protocols requested, temporarily filter
            adapters_to_scan = self._adapters
            if protocols:
                adapters_to_scan = {
                    k: v for k, v in self._adapters.items()
                    if k in protocols
                }
            
            threads = []
            for name, adapter in adapters_to_scan.items():
                duration = self._get_scan_duration(name)
                t = threading.Thread(
                    target=lambda a, d: a.start_discovery(collect_device, d),
                    args=(adapter, duration),
                    daemon=True
                )
                threads.append((t, name, duration))
                t.start()
            
            # Wait for completion
            for t, name, duration in threads:
                t.join(timeout=duration + 5)
            
        finally:
            self._discovery_callbacks.remove(collect_device)
        
        return discovered
    
    def connect_device(self, device_id: str) -> bool:
        """Connect to a specific device."""
        device = self.registry.get_device(device_id)
        if not device:
            print(f"[DiscoveryEngine] Device not found: {device_id}")
            return False
        
        adapter_name = self._get_adapter_for_protocol(device.protocol)
        if not adapter_name or adapter_name not in self._adapters:
            print(f"[DiscoveryEngine] No adapter for protocol: {device.protocol}")
            return False
        
        adapter = self._adapters[adapter_name]
        
        self.registry.update_device_state(device_id, DeviceState.CONNECTING)
        
        try:
            success = adapter.connect(device_id)
            
            if success:
                self.registry.update_device_state(device_id, DeviceState.CONNECTED)
                device = self.registry.get_device(device_id)
                if device:
                    device.mark_connected()
                    for callback in self._connection_callbacks:
                        callback(device, True)
            else:
                self.registry.update_device_state(device_id, DeviceState.ERROR)
            
            return success
            
        except Exception as e:
            print(f"[DiscoveryEngine] Connect failed: {e}")
            self.registry.update_device_state(device_id, DeviceState.ERROR)
            return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a specific device."""
        device = self.registry.get_device(device_id)
        if not device:
            return True  # Already gone
        
        adapter_name = self._get_adapter_for_protocol(device.protocol)
        if adapter_name and adapter_name in self._adapters:
            adapter = self._adapters[adapter_name]
            
            try:
                success = adapter.disconnect(device_id)
                if success:
                    self.registry.update_device_state(device_id, DeviceState.DISCONNECTED)
                    device = self.registry.get_device(device_id)
                    if device:
                        device.mark_disconnected()
                        for callback in self._connection_callbacks:
                            callback(device, False)
                return success
            except Exception as e:
                print(f"[DiscoveryEngine] Disconnect failed: {e}")
        
        return False
    
    def find_devices_by_capability(self, capability: DeviceCapability) -> List[Device]:
        """Find all devices with a specific capability."""
        return self.registry.get_devices_by_capability(capability)
    
    def find_devices_by_name(self, name_pattern: str) -> List[Device]:
        """Find devices matching a name pattern (case-insensitive)."""
        pattern = name_pattern.lower()
        return [
            d for d in self.registry.get_all_devices()
            if pattern in d.name.lower()
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current discovery engine status."""
        adapter_status = {}
        with self._adapter_lock:
            for name, adapter in self._adapters.items():
                adapter_status[name] = adapter.get_status()
        
        return {
            'mode': self.mode.name,
            'discovery_active': self._discovery_active,
            'adapters': adapter_status,
            'registry': self.registry.get_summary(),
            'last_scan': self._last_scan_time,
        }
    
    def get_all_devices(self) -> List[Device]:
        """Get all discovered devices."""
        return self.registry.get_all_devices()
    
    def get_connected_devices(self) -> List[Device]:
        """Get all currently connected devices."""
        return self.registry.get_connected_devices()
    
    def trust_device(self, device_id: str, auto_connect: bool = True):
        """Mark a device as trusted for auto-reconnection."""
        self.registry.trust_device(device_id, auto_connect)
    
    def forget_device(self, device_id: str):
        """Remove a device from the registry."""
        self.registry.remove_device(device_id)
    
    def shutdown(self):
        """Shutdown the discovery engine and all adapters."""
        print("[DiscoveryEngine] Shutting down...")
        
        self.stop_discovery()
        
        with self._adapter_lock:
            for adapter in self._adapters.values():
                adapter.shutdown()
            self._adapters.clear()
        
        print("[DiscoveryEngine] Shutdown complete.")


# Convenience function for quick device scanning
def quick_scan(protocols: Optional[List[str]] = None, duration: float = 10.0) -> List[Device]:
    """
    Perform a quick device scan and return results.
    
    Usage:
        devices = quick_scan()  # Scan all protocols
        devices = quick_scan(['bluetooth'])  # Only Bluetooth
        devices = quick_scan(['wifi', 'usb'])  # WiFi and USB
    """
    engine = DeviceDiscoveryEngine()
    engine.config.bluetooth_scan_duration = duration
    engine.config.wifi_scan_duration = duration
    engine.config.nfc_scan_duration = duration
    engine.config.usb_scan_duration = duration
    
    engine.initialize_adapters()
    devices = engine.scan_now(protocols)
    engine.shutdown()
    
    return devices
