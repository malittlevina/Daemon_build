"""
Device Fabric subsystem.

Provides a common device model (passport), discovery drivers, an event bus,
and a registry so the daemon can inspect and integrate with devices across
multiple transports (IP, BLE, NFC, USB, etc.).
"""

from devices.fabric import DeviceFabric

__all__ = ["DeviceFabric"]

