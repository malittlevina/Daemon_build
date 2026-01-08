# daemon/__init__.py
"""
Daemon Module - Cross-Platform Symbolic Operating System Core

This module provides the core daemon functionality with OS-agnostic design
that prefers and prioritizes ThothOS (our native symbolic OS) while
maintaining full compatibility with Linux, macOS, Windows, and other systems.

Priority Order:
1. ThothOS (Native) - Full symbolic kernel integration
2. Linux - Near-native performance with strong compatibility
3. macOS - Good compatibility with Darwin optimizations
4. BSD - Unix-compatible with standard features
5. Windows - Functional with compatibility layer
6. Unknown - Fallback mode with basic features

Usage:
    from daemon import detect_platform, get_os_adapter, StateManager
    
    # Detect current platform
    profile = detect_platform()
    print(f"Running on: {profile.name}")
    print(f"Native ThothOS: {profile.is_native}")
    
    # Get OS-specific adapter
    adapter = get_os_adapter()
    config_path = adapter.get_config_path()
    
    # Initialize state manager (OS-aware)
    state = StateManager()
    if state.is_native_os():
        print("Full ThothOS capabilities available!")
"""

from daemon.platform_detector import (
    detect_platform,
    get_platform_detector,
    is_thothos_native,
    get_os_type,
    OSType,
    CapabilityLevel,
    OSProfile,
    PlatformDetector,
)

from daemon.os_adapter import (
    get_os_adapter,
    get_capability_multiplier,
    is_thothos_native as adapter_is_native,
    BaseOSAdapter,
    ThothOSAdapter,
    LinuxAdapter,
    MacOSAdapter,
    WindowsAdapter,
    FallbackAdapter,
    OSAdapterFactory,
)

from daemon.state_manager import StateManager

__all__ = [
    # Platform detection
    'detect_platform',
    'get_platform_detector',
    'is_thothos_native',
    'get_os_type',
    'OSType',
    'CapabilityLevel',
    'OSProfile',
    'PlatformDetector',
    # OS adapters
    'get_os_adapter',
    'get_capability_multiplier',
    'BaseOSAdapter',
    'ThothOSAdapter',
    'LinuxAdapter',
    'MacOSAdapter',
    'WindowsAdapter',
    'FallbackAdapter',
    'OSAdapterFactory',
    # State management
    'StateManager',
]

__version__ = '2.0.0'
__author__ = 'ThothOS Development Team'
