import threading
import psutil
import os
import time

class SystemHealth:
    def __init__(self):
        self.start_time = time.time()
        self.errors = []

    def log_error(self, source: str, error_msg: str):
        self.errors.append(f"[{time.ctime()}] {source}: {error_msg}")
        if len(self.errors) > 20:
            self.errors.pop(0)

    def get_status(self):
        process = psutil.Process(os.getpid())
        uptime = time.time() - self.start_time
        
        # Thread info
        threads = threading.enumerate()
        thread_names = [t.name for t in threads]
        
        status = {
            "uptime_seconds": int(uptime),
            "memory_usage_mb": int(process.memory_info().rss / 1024 / 1024),
            "cpu_percent": process.cpu_percent(),
            "active_threads_count": len(threads),
            "active_threads": thread_names,
            "recent_errors": self.errors[-5:]
        }
        return status

    def format_status(self):
        s = self.get_status()
        report = [
            "--- System Health Report ---",
            f"Uptime: {s['uptime_seconds']}s",
            f"Memory: {s['memory_usage_mb']} MB",
            f"CPU: {s['cpu_percent']}%",
            f"Threads: {s['active_threads_count']} ({', '.join(s['active_threads'])})",
            "--- Recent Errors ---"
        ]
        if s['recent_errors']:
            report.extend(s['recent_errors'])
        else:
            report.append("None")
        return "\n".join(report)

# Singleton
_HEALTH_INSTANCE = None
def get_system_health():
    global _HEALTH_INSTANCE
    if _HEALTH_INSTANCE is None:
        _HEALTH_INSTANCE = SystemHealth()
    return _HEALTH_INSTANCE
