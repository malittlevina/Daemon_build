import time

class Unimind:
    def __init__(self):
        self.modules = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": []
        }
        print("[Unimind] Core initialized.")

    def register(self, type, module):
        if type in self.modules:
            self.modules[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")
        else:
            print(f"[Unimind] Warning: Unknown module type '{type}'")

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        
        # 1. Gather Context
        context = {}
        
        # Check emotional state if available
        if self.modules["emotion"]:
            # Assuming the first emotion module is the primary engine
            emotion_engine = self.modules["emotion"][0]
            # Check if it has the new dictionary state or old string state
            if hasattr(emotion_engine, "state") and isinstance(emotion_engine.state, dict):
                 # New PAD model
                 context["emotion"] = emotion_engine.get_emotion_name()
                 context["pad"] = emotion_engine.state
            else:
                 # Fallback or old model
                 context["emotion"] = emotion_engine.get_emotion()

        print(f"[Unimind] Context gathered: {context}")

        # 2. Logic Processing based on Context
        # (Simulating thought patterns based on emotion)
        if "pad" in context:
            p, a, d = context["pad"]["pleasure"], context["pad"]["arousal"], context["pad"]["dominance"]
            if p < -0.3:
                print("[Unimind] Focus: Fixing errors and stabilization (Negative Pleasure detected).")
            elif a > 0.5:
                print("[Unimind] Focus: Exploration and high-energy tasks (High Arousal detected).")
            else:
                print("[Unimind] Focus: Routine maintenance and optimization.")

        # 3. Execute Logic Modules
        for logic_module in self.modules["logic"]:
            if hasattr(logic_module, "think"):
                logic_module.think(context)
