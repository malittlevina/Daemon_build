# memory_tree/memory_logger.py
import json
import os
from datetime import datetime, timezone

class MemoryLogger:
    def __init__(self, log_dir="memory_tree/logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "memory_log.json")

    def log_event(self, event_type, content, context=None):
        # Use timezone-aware UTC timestamps (avoids deprecated utcnow()).
        timestamp = datetime.now(timezone.utc).isoformat()
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

# Global helpers for external imports
def log_memory(content, context=None):
    logger = MemoryLogger()
    logger.log_event("memory", content, context=context)
    print(f"[MemoryLogger] Logged memory: {content}")

def retrieve_log():
    logger = MemoryLogger()
    return logger.get_latest_events(50)
