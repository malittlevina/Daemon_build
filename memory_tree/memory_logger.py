import json
import os
import time
from datetime import datetime

class MemoryLogger:
    def __init__(self, log_dir="memory_tree/logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "memory_log.json")
        self.max_history = 100
        
        # Ensure log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_event(self, event_type, content, context=None, importance=1.0):
        timestamp = datetime.utcnow().isoformat()
        
        # Simple importance weighting
        if importance < 0.1:
            print(f"[MemoryLogger] Ignoring trivial event: {content}")
            return

        log_entry = {
            "id": f"{int(time.time()*1000)}",
            "timestamp": timestamp,
            "type": event_type,
            "content": content,
            "context": context or {},
            "importance": importance
        }
        self._append_log(log_entry)

    def _append_log(self, entry):
        try:
            with open(self.log_file, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
            
            data.append(entry)
            
            # Prune old low-importance memories if file gets too big
            if len(data) > self.max_history:
                # Sort by importance (keep high importance), then timestamp
                # Actually, simpler: just keep the last N events for now
                data = data[-self.max_history:]
            
            with open(self.log_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[MemoryLogger] Error writing log: {e}")

    def get_latest_events(self, count=5, min_importance=0.0):
        if not os.path.exists(self.log_file):
            return []
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
                
            filtered = [d for d in data if d.get("importance", 1.0) >= min_importance]
            return filtered[-count:]
        except Exception:
            return []

    def recall_by_context(self, context_key, context_value):
        # Basic associative recall
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
            
            results = []
            for entry in data:
                ctx = entry.get("context", {})
                if ctx.get(context_key) == context_value:
                    results.append(entry)
            return results
        except Exception:
            return []

# Singleton / Global helpers
_memory_instance = MemoryLogger()

def log_memory(content, context=None, importance=1.0):
    _memory_instance.log_event("memory", content, context=context, importance=importance)
    print(f"[MemoryLogger] Logged: {content}")

def retrieve_log():
    return _memory_instance.get_latest_events(50)
