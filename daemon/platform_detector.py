# daemon/platform_detector.py
"""
Platform Detection and OS Preference System

This module enables the daemon to run on any operating system while
prioritizing and optimizing for ThothOS (our native symbolic OS).

Hierarchy of OS Preference:
1. ThothOS (Native) - Full symbolic integration, maximum capabilities
2. Linux - Strong compatibility, near-native performance
3. macOS - Good compatibility with some adaptations
4. Windows - Functional with compatibility layer
5. Other/Unknown - Basic fallback mode
"""

import os
import sys
import platform
import subprocess
from enum import Enum, auto
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass


class OSType(Enum):
    """Enumeration of supported operating systems."""
    THOTHOS = auto()      # Native symbolic OS - highest priority
    LINUX = auto()        # Strong compatibility
    MACOS = auto()        # Darwin-based systems
    WINDOWS = auto()      # Windows with compatibility layer
    BSD = auto()          # BSD variants
    UNKNOWN = auto()      # Fallback mode


class CapabilityLevel(Enum):
    """Capability levels based on OS context."""
    NATIVE = auto()       # Full ThothOS integration
    ENHANCED = auto()     # Near-native on compatible systems
    STANDARD = auto()     # Standard functionality
    LIMITED = auto()      # Reduced capabilities
    FALLBACK = auto()     # Minimal functionality


@dataclass
class OSProfile:
    """Profile describing OS capabilities and preferences."""
    os_type: OSType
    capability_level: CapabilityLevel
    name: str
    version: str
    architecture: str
    is_native: bool
    priority_score: int  # Higher = more preferred (ThothOS = 100)
    available_features: List[str]
    limitations: List[str]


class PlatformDetector:
    """
    Detects the current operating system and determines capability levels.
    Prioritizes ThothOS while maintaining cross-platform compatibility.
    """
    
    # ThothOS signature files/markers
    THOTHOS_MARKERS = [
        "/etc/thothos-release",
        "/var/lib/thothos/.daemon_native",
        "/.thothos_root",
        os.path.expanduser("~/.thothos/native_mode"),
    ]
    
    # Feature availability by OS
    FEATURE_MATRIX = {
        OSType.THOTHOS: [
            "symbolic_kernel_access",
            "native_scroll_triggers",
            "deep_memory_integration",
            "realtime_emotion_sync",
            "hardware_sensor_direct",
            "ritual_system_hooks",
            "kernel_reflection",
            "symbolic_ipc",
            "daemon_persistence",
            "hot_reload",
        ],
        OSType.LINUX: [
            "native_scroll_triggers",
            "deep_memory_integration",
            "realtime_emotion_sync",
            "hardware_sensor_direct",
            "daemon_persistence",
            "hot_reload",
        ],
        OSType.MACOS: [
            "native_scroll_triggers",
            "deep_memory_integration",
            "realtime_emotion_sync",
            "daemon_persistence",
        ],
        OSType.WINDOWS: [
            "deep_memory_integration",
            "daemon_persistence",
        ],
        OSType.BSD: [
            "native_scroll_triggers",
            "deep_memory_integration",
            "daemon_persistence",
        ],
        OSType.UNKNOWN: [
            "basic_operation",
        ],
    }
    
    # Priority scores (higher = more preferred)
    PRIORITY_SCORES = {
        OSType.THOTHOS: 100,
        OSType.LINUX: 85,
        OSType.MACOS: 75,
        OSType.BSD: 70,
        OSType.WINDOWS: 60,
        OSType.UNKNOWN: 30,
    }
    
    def __init__(self):
        self._cached_profile: Optional[OSProfile] = None
        self._detection_hooks: List[Callable] = []
        self._os_adapters: Dict[OSType, object] = {}
        
    def detect(self) -> OSProfile:
        """
        Detect the current operating system and build a capability profile.
        Returns cached profile if already detected.
        """
        if self._cached_profile:
            return self._cached_profile
            
        # First, check for ThothOS (highest priority)
        if self._is_thothos():
            self._cached_profile = self._build_thothos_profile()
        else:
            # Fall back to standard OS detection
            system = platform.system().lower()
            
            if system == "linux":
                self._cached_profile = self._build_linux_profile()
            elif system == "darwin":
                self._cached_profile = self._build_macos_profile()
            elif system == "windows":
                self._cached_profile = self._build_windows_profile()
            elif "bsd" in system:
                self._cached_profile = self._build_bsd_profile()
            else:
                self._cached_profile = self._build_unknown_profile()
        
        # Run any registered detection hooks
        for hook in self._detection_hooks:
            try:
                hook(self._cached_profile)
            except Exception as e:
                print(f"[PlatformDetector] Warning: Detection hook failed: {e}")
                
        return self._cached_profile
    
    def _is_thothos(self) -> bool:
        """Check if we're running on ThothOS."""
        # Check for ThothOS marker files
        for marker in self.THOTHOS_MARKERS:
            if os.path.exists(marker):
                return True
        
        # Check environment variable
        if os.environ.get("THOTHOS_NATIVE", "").lower() == "true":
            return True
            
        # Check for ThothOS in uname (if available)
        try:
            uname = platform.uname()
            if "thothos" in uname.system.lower() or "thothos" in uname.release.lower():
                return True
        except:
            pass
            
        # Check for ThothOS daemon socket
        if os.path.exists("/run/thothos/daemon.sock"):
            return True
            
        return False
    
    def _build_thothos_profile(self) -> OSProfile:
        """Build profile for native ThothOS environment."""
        return OSProfile(
            os_type=OSType.THOTHOS,
            capability_level=CapabilityLevel.NATIVE,
            name="ThothOS",
            version=self._get_thothos_version(),
            architecture=platform.machine(),
            is_native=True,
            priority_score=self.PRIORITY_SCORES[OSType.THOTHOS],
            available_features=self.FEATURE_MATRIX[OSType.THOTHOS],
            limitations=[],
        )
    
    def _build_linux_profile(self) -> OSProfile:
        """Build profile for Linux systems."""
        distro = self._get_linux_distro()
        return OSProfile(
            os_type=OSType.LINUX,
            capability_level=CapabilityLevel.ENHANCED,
            name=f"Linux ({distro})",
            version=platform.release(),
            architecture=platform.machine(),
            is_native=False,
            priority_score=self.PRIORITY_SCORES[OSType.LINUX],
            available_features=self.FEATURE_MATRIX[OSType.LINUX],
            limitations=["no_symbolic_kernel", "no_kernel_reflection"],
        )
    
    def _build_macos_profile(self) -> OSProfile:
        """Build profile for macOS systems."""
        return OSProfile(
            os_type=OSType.MACOS,
            capability_level=CapabilityLevel.STANDARD,
            name="macOS",
            version=platform.mac_ver()[0],
            architecture=platform.machine(),
            is_native=False,
            priority_score=self.PRIORITY_SCORES[OSType.MACOS],
            available_features=self.FEATURE_MATRIX[OSType.MACOS],
            limitations=["no_symbolic_kernel", "no_kernel_reflection", "limited_sensors"],
        )
    
    def _build_windows_profile(self) -> OSProfile:
        """Build profile for Windows systems."""
        return OSProfile(
            os_type=OSType.WINDOWS,
            capability_level=CapabilityLevel.LIMITED,
            name="Windows",
            version=platform.version(),
            architecture=platform.machine(),
            is_native=False,
            priority_score=self.PRIORITY_SCORES[OSType.WINDOWS],
            available_features=self.FEATURE_MATRIX[OSType.WINDOWS],
            limitations=[
                "no_symbolic_kernel",
                "no_kernel_reflection", 
                "limited_sensors",
                "no_native_scrolls",
                "compatibility_layer_required",
            ],
        )
    
    def _build_bsd_profile(self) -> OSProfile:
        """Build profile for BSD systems."""
        return OSProfile(
            os_type=OSType.BSD,
            capability_level=CapabilityLevel.STANDARD,
            name=f"BSD ({platform.system()})",
            version=platform.release(),
            architecture=platform.machine(),
            is_native=False,
            priority_score=self.PRIORITY_SCORES[OSType.BSD],
            available_features=self.FEATURE_MATRIX[OSType.BSD],
            limitations=["no_symbolic_kernel", "no_kernel_reflection", "limited_sensors"],
        )
    
    def _build_unknown_profile(self) -> OSProfile:
        """Build fallback profile for unknown systems."""
        return OSProfile(
            os_type=OSType.UNKNOWN,
            capability_level=CapabilityLevel.FALLBACK,
            name=platform.system() or "Unknown",
            version=platform.release() or "Unknown",
            architecture=platform.machine() or "Unknown",
            is_native=False,
            priority_score=self.PRIORITY_SCORES[OSType.UNKNOWN],
            available_features=self.FEATURE_MATRIX[OSType.UNKNOWN],
            limitations=["fallback_mode", "limited_functionality"],
        )
    
    def _get_thothos_version(self) -> str:
        """Get ThothOS version from release file."""
        try:
            for marker in self.THOTHOS_MARKERS:
                if os.path.exists(marker) and "release" in marker:
                    with open(marker, "r") as f:
                        return f.read().strip()
        except:
            pass
        return os.environ.get("THOTHOS_VERSION", "1.0.0")
    
    def _get_linux_distro(self) -> str:
        """Get Linux distribution name."""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=")[1].strip().strip('"')
        except:
            pass
        return "Generic"
    
    def has_feature(self, feature: str) -> bool:
        """Check if a specific feature is available on the current platform."""
        profile = self.detect()
        return feature in profile.available_features
    
    def get_capability_level(self) -> CapabilityLevel:
        """Get the current capability level."""
        return self.detect().capability_level
    
    def is_native(self) -> bool:
        """Check if running on native ThothOS."""
        return self.detect().is_native
    
    def register_detection_hook(self, hook: Callable) -> None:
        """Register a callback to be executed after detection."""
        self._detection_hooks.append(hook)
    
    def get_os_priority(self) -> int:
        """Get the priority score for the current OS (higher = better)."""
        return self.detect().priority_score
    
    def should_enable_feature(self, feature: str, fallback: bool = False) -> bool:
        """
        Determine if a feature should be enabled based on OS capabilities.
        Returns fallback value if feature is not explicitly supported.
        """
        profile = self.detect()
        if feature in profile.available_features:
            return True
        if feature in profile.limitations:
            return False
        return fallback


# Global singleton instance
_detector: Optional[PlatformDetector] = None


def get_platform_detector() -> PlatformDetector:
    """Get or create the global platform detector instance."""
    global _detector
    if _detector is None:
        _detector = PlatformDetector()
    return _detector


def detect_platform() -> OSProfile:
    """Convenience function to detect the current platform."""
    return get_platform_detector().detect()


def is_thothos_native() -> bool:
    """Convenience function to check if running on native ThothOS."""
    return get_platform_detector().is_native()


def get_os_type() -> OSType:
    """Convenience function to get the current OS type."""
    return get_platform_detector().detect().os_type
