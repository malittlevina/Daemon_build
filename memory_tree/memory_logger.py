from core.module import Module
import json
import os
from datetime import datetime

class MemoryLogger(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.log_dir = "memory_tree/logs"
        self.log_file = os.path.join(self.log_dir, "memory_log.json")

    def initialize(self):
        os.makedirs(self.log_dir, exist_ok=True)
        print("[MemoryLogger] Initialized.")
        self.kernel.events.subscribe("log", self.handle_log_event)

    def start(self):
        pass

    def stop(self):
        pass

    def handle_log_event(self, event_type, data):
        self.log_event(data.get("type", "info"), data.get("content"), data.get("context"))

    def log_event(self, event_type, content, context=None):
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": event_type,
            "content": content,
            "context": context
        }
        self._append_log(log_entry)

    def _append_log(self, entry):
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(entry)
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_latest_events(self, count=5):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []
        return data[-count:]

# Global helpers for external imports - DEPRECATED in favor of Kernel
def log_memory(content, context=None):
    # This creates a detached instance without kernel. 
    # Ideally should use the kernel's memory module.
    # For now, we patch it to work standalone for backward compat if needed,
    # but we cannot pass 'kernel' here easily without a global kernel reference.
    # We will assume callers will be migrated or this will just work for file I/O.
    logger = MemoryLogger(None) 
    logger.log_dir = "memory_tree/logs"
    logger.log_file = os.path.join(logger.log_dir, "memory_log.json")
    # Manually ensure dir exists since initialize isn't called
    os.makedirs(logger.log_dir, exist_ok=True)
    
    logger.log_event("memory", content, context=context)
    print(f"[MemoryLogger] Logged memory: {content}")

def retrieve_log():
    logger = MemoryLogger(None)
    logger.log_dir = "memory_tree/logs"
    logger.log_file = os.path.join(logger.log_dir, "memory_log.json")
    return logger.get_latest_events(50)
