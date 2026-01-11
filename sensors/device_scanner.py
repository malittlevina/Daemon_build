import time
import subprocess
import threading
import json
import random

class DeviceScanner:
    def __init__(self):
        self.known_devices = {}
        self.scanning_active = False
        self._lock = threading.Lock()
        self.listeners = []

    def add_listener(self, callback):
        """Adds a callback function to be called when a new device is found.
           Callback signature: callback(device_info)
        """
        self.listeners.append(callback)

    def _notify_listeners(self, device):
        for listener in self.listeners:
            try:
                listener(device)
            except Exception as e:
                print(f"[DeviceScanner] Listener error: {e}")

    def start_scanning(self, interval=60):
        """Starts the scanning process in a background thread."""
        self.scanning_active = True
        thread = threading.Thread(target=self._scan_loop, args=(interval,), daemon=True)
        thread.start()
        print("[DeviceScanner] Background scanning started.")

    def stop_scanning(self):
        self.scanning_active = False
        print("[DeviceScanner] Background scanning stopped.")

    def _scan_loop(self, interval):
        while self.scanning_active:
            self.scan_all()
            time.sleep(interval)

    def scan_all(self):
        """Scans for all supported device types."""
        results = {
            "bluetooth": self.scan_bluetooth(),
            "wifi": self.scan_wifi(),
            "nfc": self.scan_nfc()
        }
        
        with self._lock:
            # Merge results into known_devices
            for dev_type, devices in results.items():
                for dev in devices:
                    dev_id = dev.get("id") or dev.get("mac") or dev.get("ssid")
                    if dev_id:
                        if dev_id not in self.known_devices:
                             print(f"[DeviceScanner] New {dev_type} device found: {dev_id}")
                             self._notify_listeners(dev)
                        self.known_devices[dev_id] = dev
                        self.known_devices[dev_id]["last_seen"] = time.time()
                        self.known_devices[dev_id]["type"] = dev_type

        return results

    def scan_bluetooth(self):
        """Scans for Bluetooth devices (Simulated if libs missing)."""
        devices = []
        try:
            # Attempt to use bluetoothctl (Linux) if available
            # This is a basic implementation and might fail in container without hardware access
            # So we wrap in try/except and fallback to simulation for dev environment
            cmd = "bluetoothctl devices"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    parts = line.split(" ", 2)
                    if len(parts) >= 3:
                        devices.append({"mac": parts[1], "name": parts[2]})
        except Exception:
            pass

        # Simulation for development/testing if no devices found or error
        if not devices:
            # Simulate a device occasionally
            if random.random() < 0.3: 
                devices.append({
                    "mac": f"00:11:22:33:44:{random.randint(10,99)}", 
                    "name": f"Test Device {random.randint(1, 100)}"
                })
        
        return devices

    def scan_wifi(self):
        """Scans for Wi-Fi networks (Simulated if libs missing)."""
        networks = []
        try:
            # Attempt to use nmcli (Linux)
            cmd = "nmcli -t -f SSID,BSSID,SIGNAL dev wifi list"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    parts = line.split(":")
                    if parts[0]: # Has SSID
                         networks.append({"ssid": parts[0], "bssid": ":".join(parts[1:7] if len(parts)>6 else parts[1:]), "signal": parts[-1]})
        except Exception:
            pass

        if not networks:
            if random.random() < 0.3:
                networks.append({"ssid": f"Home_Network_{random.randint(1,10)}", "signal": random.randint(50, 90)})

        return networks

    def scan_nfc(self):
        """Checks for NFC tags (Simulated)."""
        # NFC usually requires polling specific hardware libraries like nfcpy
        # or reading from a character device.
        tags = []
        # Simulation
        if random.random() < 0.1:
            tags.append({"id": f"NFC_{random.randint(1000,9999)}", "data": "Access Token"})
        return tags

    def get_known_devices(self):
        with self._lock:
            return self.known_devices.copy()

    def connect_device(self, device_id):
        """Attempt to connect to a device by ID."""
        device = self.known_devices.get(device_id)
        if not device:
            return False, "Device not found"
        
        print(f"[DeviceScanner] Attempting to connect to {device.get('name', device_id)}...")
        # Logic to connect would go here (pairing, auth, etc.)
        # For now, we simulate success
        time.sleep(1)
        return True, "Connected successfully (Simulated)"
