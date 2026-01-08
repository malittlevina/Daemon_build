import os
import sys
import platform
import logging

class PlatformManager:
    def __init__(self):
        self.os_type = self._detect_os()
        self.is_native = self._check_native_environment()
        self.logger = logging.getLogger("PlatformManager")
    
    def _detect_os(self):
        """Detects the underlying operating system."""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def _check_native_environment(self):
        """
        Checks if the daemon is running within the native ThothOS environment.
        This prioritizes our custom OS.
        """
        # Check for environment variable
        if os.environ.get("THOTH_OS_ACTIVE") == "1":
            return True
        
        # Check for specific system file (simulated for now)
        if os.path.exists("/etc/thoth_release"):
            return True
            
        return False

    def get_platform_info(self):
        return {
            "os": self.os_type,
            "is_native": self.is_native,
            "architecture": platform.machine(),
            "node": platform.node()
        }

    def get_optimization_profile(self):
        """
        Returns configuration overrides based on the platform.
        Prioritizes ThothOS with 'native' profile.
        """
        if self.is_native:
            self.logger.info("Native ThothOS environment detected. Applying high-priority optimization.")
            return {
                "performance_mode": "high",
                "resource_limit": "unrestricted",
                "integration_level": "deep",
                "modules_enabled": ["all"]
            }
        else:
            self.logger.info(f"Running on {self.os_type} (Guest Mode). Applying standard compatibility profile.")
            return {
                "performance_mode": "balanced",
                "resource_limit": "standard",
                "integration_level": "surface",
                "modules_enabled": ["core", "bridge"]
            }

    def apply_optimizations(self):
        """
        Apply system-level optimizations if allowed.
        """
        if self.is_native:
            # Placeholder for native OS specific tuning
            pass
        elif self.os_type == "linux":
            # Linux specific adjustments
            pass
