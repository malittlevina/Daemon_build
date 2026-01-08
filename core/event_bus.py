import threading
import collections

class EventBus:
    def __init__(self):
        self.subscribers = collections.defaultdict(list)
        self.lock = threading.Lock()

    def subscribe(self, event_type, callback):
        """
        Subscribe a callback to an event type.
        Callback should accept (event_type, data).
        """
        with self.lock:
            self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        """
        Publish an event to all subscribers.
        """
        with self.lock:
            # Copy list to allow modification during iteration if needed (though dangerous)
            callbacks = self.subscribers.get(event_type, [])[:]
        
        for callback in callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"[EventBus] Error in subscriber for {event_type}: {e}")

    def unsubscribe(self, event_type, callback):
        with self.lock:
            if event_type in self.subscribers:
                try:
                    self.subscribers[event_type].remove(callback)
                except ValueError:
                    pass
