import psutil
import subprocess
import os
import platform
import datetime

class KernelBridge:
    def __init__(self):
        self.os_type = platform.system()
        print(f"[KernelBridge] Initialized on {self.os_type}")

    def get_system_stats(self):
        """Returns critical system metrics."""
        stats = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage(os.path.abspath(os.sep)).percent,
            "uptime_seconds": int(datetime.datetime.now().timestamp() - psutil.boot_time())
        }
        
        # Battery (if applicable)
        battery = psutil.sensors_battery()
        if battery:
            stats["battery_percent"] = battery.percent
            stats["power_plugged"] = battery.power_plugged
            
        return stats

    def list_processes(self, limit=10, sort_by="cpu"):
        """Lists top processes."""
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort
        if sort_by == "memory":
            procs.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
        else:
            procs.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
        return procs[:limit]

    def execute_command(self, command, timeout=30):
        """Executes a shell command safely."""
        print(f"[KernelBridge] Executing: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_environment_info(self):
        return {
            "os": self.os_type,
            "release": platform.release(),
            "python_version": platform.python_version(),
            "cwd": os.getcwd(),
            "user": os.getlogin() if hasattr(os, "getlogin") else "unknown"
        }
