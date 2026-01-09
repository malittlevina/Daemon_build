from core.module import Module

class RitualRegistry(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        # Static rituals (hardcoded)
        self.registered_rituals = {
            "optimize self": self.cast_optimize_self,
            "summon knowledge": self.cast_codex_query
        }
        # Dynamic rituals (added at runtime)
        self.dynamic_rituals = {}

    def initialize(self):
        self.kernel.log("RitualRegistry", "Initialized.")

    def start(self):
        pass

    def stop(self):
        pass

    def get_scroll_engine(self):
        return self.kernel.get_module("scrolls")

    # ---- Static Rituals ----
    def cast_ritual(self, ritual_name: str, context: dict = {}):
        if ritual_name in self.registered_rituals:
            return self.registered_rituals[ritual_name](context)
        elif ritual_name in self.dynamic_rituals:
            self.kernel.log("RitualRegistry", f"Invoking dynamic ritual: {ritual_name}")
            return self.dynamic_rituals[ritual_name]["action"]()
        else:
            return f"Unknown ritual: {ritual_name}"

    def cast_optimize_self(self, context):
        engine = self.get_scroll_engine()
        if engine:
            return engine.invoke("optimize self", *[], **context)
        return "Scroll Engine not available"

    def cast_codex_query(self, context):
        engine = self.get_scroll_engine()
        if engine:
            return engine.invoke("summon scroll summary", *[], **context)
        return "Scroll Engine not available"

    # ---- Dynamic Rituals ----
    def register(self, name, trigger, action):
        self.dynamic_rituals[name] = {"trigger": trigger, "action": action}
        self.kernel.log("RitualRegistry", f"Ritual '{name}' registered.")

    def evaluate_triggers(self):
        for name, ritual in self.dynamic_rituals.items():
            if ritual["trigger"]():
                self.kernel.log("RitualRegistry", f"Auto-invoking triggered ritual: {name}")
                ritual["action"]()
