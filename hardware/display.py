import platform
import subprocess
import re
import shutil
from typing import Dict, List, Optional

class DisplayManager:
    def __init__(self):
        self.os_type = platform.system()
        self.displays = []
        self.current_settings = {}

    def scan_displays(self) -> List[Dict]:
        """
        Detects connected displays and their capabilities.
        """
        self.displays = []
        if self.os_type == "Linux":
            self._scan_linux()
        elif self.os_type == "Windows":
            self._scan_windows_stub()
        elif self.os_type == "Darwin": # macOS
            self._scan_mac_stub()
            
        return self.displays

    def _scan_linux(self):
        # Use xrandr if available
        if not shutil.which("xrandr"):
            print("[DisplayManager] xrandr not found.")
            return

        try:
            output = subprocess.check_output(["xrandr", "--verbose"]).decode("utf-8")
            # Simple parser for connected displays
            # Looking for "HDMI-1 connected 1920x1080+0+0"
            current_display = None
            
            for line in output.split("\n"):
                if " connected" in line:
                    parts = line.split()
                    name = parts[0]
                    is_primary = "primary" in line
                    
                    # Try to parse current resolution
                    resolution = "Unknown"
                    for part in parts:
                        if "x" in part and "+" in part:
                            resolution = part.split("+")[0]
                    
                    current_display = {
                        "name": name,
                        "primary": is_primary,
                        "current_res": resolution,
                        "modes": []
                    }
                    self.displays.append(current_display)
                
                elif current_display and "  " in line and "x" in line:
                    # Parse available modes (e.g., "  1920x1080 (0x...)")
                    mode = line.strip().split()[0]
                    current_display["modes"].append(mode)
                    
        except Exception as e:
            print(f"[DisplayManager] Error scanning Linux displays: {e}")

    def _scan_windows_stub(self):
        # Stub for Windows implementation using ctypes or PowerShell
        self.displays.append({
            "name": "Generic PnP Monitor",
            "current_res": "1920x1080",
            "modes": ["1920x1080", "1280x720"]
        })

    def _scan_mac_stub(self):
        self.displays.append({
            "name": "Built-in Retina Display",
            "current_res": "2560x1600",
            "modes": ["2560x1600", "1920x1200"]
        })

    def set_resolution(self, display_name: str, width: int, height: int):
        """
        Applies resolution settings.
        """
        print(f"[DisplayManager] Setting {display_name} to {width}x{height}...")
        
        if self.os_type == "Linux":
            cmd = ["xrandr", "--output", display_name, "--mode", f"{width}x{height}"]
            try:
                subprocess.run(cmd, check=True)
                return True
            except subprocess.CalledProcessError as e:
                print(f"[DisplayManager] Failed to set resolution: {e}")
                return False
        
        return False # Not implemented for other OS in this demo

    def adjust_gamma_brightness(self, display_name: str, brightness: float = 1.0, gamma: str = "1.0:1.0:1.0"):
        """
        Adjusts brightness/contrast/gamma via software (xrandr).
        brightness: 0.0 to 1.0 (or higher)
        gamma: R:G:B float string
        """
        if self.os_type == "Linux":
            cmd = ["xrandr", "--output", display_name, "--brightness", str(brightness), "--gamma", gamma]
            try:
                subprocess.run(cmd, check=True)
                print(f"[DisplayManager] Adjusted brightness to {brightness} and gamma to {gamma}")
                return True
            except Exception as e:
                print(f"[DisplayManager] Failed to adjust visual settings: {e}")
                return False
        return False
