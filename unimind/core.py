class Unimind:
    def __init__(self):
        self.modules = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": []
        }
        self.subscribers = {}
        print("[Unimind] Core initialized. Event Bus active.")

    def register(self, type, module):
        if type in self.modules:
            self.modules[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")

    def subscribe(self, event_type, callback):
        """Register a callback for a specific event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def emit(self, event_type, payload):
        """Emit an event to all subscribers."""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    print(f"[Unimind] Error in subscriber for '{event_type}': {e}")

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        for logic_module in self.modules["logic"]:
            logic_module.think()
