from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    timestamp: float = 0.0
    source: str = "system"

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = datetime.now().timestamp()

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self.history: List[Event] = []

    def subscribe(self, event_type: str, callback: Callable[[Event], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"[EventBus] Subscribed to '{event_type}'")

    def publish(self, event_type: str, payload: Dict[str, Any] = {}, source: str = "system"):
        event = Event(event_type, payload, source=source)
        self.history.append(event)
        
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[EventBus Error] Callback failed for '{event_type}': {e}")
        
        # Also publish to wildcard listeners (optional, but good for logging)
        if "*" in self.subscribers:
            for callback in self.subscribers["*"]:
                callback(event)

    def get_history(self, limit: int = 10) -> List[Event]:
        return self.history[-limit:]
