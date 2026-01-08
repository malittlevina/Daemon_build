from core.module import Module

class Unimind(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.modules = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": []
        }

    def initialize(self):
        print("[Unimind] Core initialized.")
        # Subscribe to relevant kernel events
        self.kernel.events.subscribe("user_input", self.handle_input)

    def start(self):
        print("[Unimind] Reasoning engine started.")

    def stop(self):
        print("[Unimind] Reasoning engine stopped.")

    def register(self, type, module):
        if type in self.modules:
            self.modules[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        for logic_module in self.modules["logic"]:
            logic_module.think()

    def handle_input(self, event_type, data):
        # Example handler
        print(f"[Unimind] Observed input: {data}")
