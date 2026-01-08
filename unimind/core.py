class Unimind:
    def __init__(self, context=None):
        self.context = context or {}
        self.modules = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": []
        }
        print("[Unimind] Core initialized.")
        if self.context.get("is_native_os"):
             print("[Unimind] Native OS detected. Optimizing decision matrix.")

    def register(self, type, module):
        if type in self.modules:
            self.modules[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        for logic_module in self.modules["logic"]:
            logic_module.think()
