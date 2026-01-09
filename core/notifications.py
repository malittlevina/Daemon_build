from core.module import Module
import time
import uuid

class NotificationManager(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.queue = [] # List of {id, title, message, level, timestamp}
        self.history = []

    def initialize(self):
        self.kernel.log("NotificationManager", "Initialized.")
        self.kernel.events.subscribe("system:notify", self.on_notification)

    def start(self):
        pass

    def stop(self):
        pass

    def on_notification(self, event_type, data):
        self.notify(data.get("title", "System"), data.get("message", ""), data.get("level", "info"))

    def notify(self, title, message, level="info"):
        note = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "message": message,
            "level": level,
            "timestamp": time.time(),
            "read": False
        }
        self.queue.append(note)
        self.history.append(note)
        self.kernel.log("NotificationManager", f"[{level.upper()}] {title}: {message}")
        
        # If we had a sound system, we'd play a sound here.
        
    def get_unread(self):
        unread = [n for n in self.queue if not n["read"]]
        return unread

    def mark_all_read(self):
        for n in self.queue:
            n["read"] = True
        self.queue = [] # Clear active queue, keep history
        return "All notifications marked read."
