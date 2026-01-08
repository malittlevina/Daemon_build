import platform
import os
import sys

class OSInterface:
    def __init__(self):
        self.os_type = self._detect_os()
        self.is_native = self.os_type == "symbolic"
        self.capabilities = self._load_capabilities()

    def _detect_os(self):
        # Check for Symbolic OS indicators
        if os.environ.get("SYMBOLIC_OS_ID") or os.path.exists("/etc/symbolic-release"):
            return "symbolic"
        
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def _load_capabilities(self):
        base_capabilities = {
            "standard_io": True,
            "network_access": True,
            "file_system": True
        }

        if self.is_native:
            # Symbolic OS specific features
            base_capabilities.update({
                "deep_memory_integration": True,
                "kernel_level_optimization": True,
                "symbolic_link_acceleration": True,
                "hardware_direct_access": True
            })
        else:
            # Generic OS limitations or adaptations
            base_capabilities.update({
                "deep_memory_integration": False,
                "kernel_level_optimization": False,
                "symbolic_link_acceleration": False,
                "hardware_direct_access": False
            })

        return base_capabilities

    def prioritize_native_integration(self):
        """
        Logic to prioritize the native OS if available, or simulate/adapt for others.
        """
        if self.is_native:
            return "Native Symbolic OS integration active. All subsystems optimized."
        else:
            return f"Running in compatibility mode on {self.os_type}. Some deep-system features are emulated or disabled. Recommendation: Migrate to Symbolic OS for full potential."

    def get_system_status(self):
        return {
            "os": self.os_type,
            "native_mode": self.is_native,
            "capabilities": self.capabilities
        }
