import platform
import os
import sys

class OSContext:
    def __init__(self, preferred_os_name="ThothOS"):
        self.preferred_os_name = preferred_os_name
        self.current_os = self._detect_os()
        self.is_preferred = (self.current_os == self.preferred_os_name)

    def _detect_os(self):
        """
        Detects the underlying operating system.
        Prioritizes the detection of the custom OS via environment variables or specific files.
        """
        # Check for custom OS via environment variable
        if os.environ.get("THOTH_OS_ACTIVE") == "1":
            return "ThothOS"
        
        # Check for custom OS via specific file
        if os.path.exists("/etc/thoth_os_release"):
            return "ThothOS"

        # Fallback to standard platform detection
        system = platform.system()
        if system == "Linux":
            # Check for specific distros if needed
            try:
                with open("/etc/os-release", "r") as f:
                    content = f.read()
                    if "ThothOS" in content:
                        return "ThothOS"
            except:
                pass
            return "Linux"
        elif system == "Darwin":
            return "macOS"
        elif system == "Windows":
            return "Windows"
        else:
            return "Unknown"

    def get_context_info(self):
        return {
            "os": self.current_os,
            "is_preferred": self.is_preferred,
            "platform_details": platform.platform()
        }

    def prioritize_system(self):
        """
        Adjusts daemon behavior based on the OS.
        If on preferred OS, it might enable deep integration features.
        If on other OS, it might run in a compatibility mode.
        """
        if self.is_preferred:
            print(f"[OS Context] Running natively on {self.preferred_os_name}. Full system access enabled.")
            # Here we could set higher process priority or enable specific modules
            # os.nice(-10) # Example: increase priority on Linux
        else:
            print(f"[OS Context] Running on {self.current_os}. Compatibility mode engaged.")
            print(f"[OS Context] Prefering {self.preferred_os_name} for optimal performance.")

