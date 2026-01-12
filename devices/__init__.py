# devices/__init__.py
"""
Device Connection Protocol Module
=================================
Provides unified device discovery, connection, and management
across multiple protocols: Bluetooth, WiFi, NFC, USB, and more.

This module is AI-native, designed to be managed by intelligent agents
that can seamlessly detect, inspect, and integrate with any connected device.
"""

from .device_registry import DeviceRegistry, Device, DeviceCapability
from .discovery_engine import DeviceDiscoveryEngine
from .device_bridge import DeviceBridge

__all__ = [
    'DeviceRegistry',
    'Device', 
    'DeviceCapability',
    'DeviceDiscoveryEngine',
    'DeviceBridge'
]
