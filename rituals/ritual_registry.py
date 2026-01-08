# rituals/ritual_registry.py

from scrolls.scroll_engine import ScrollEngine

class RitualRegistry:
    def __init__(self):
        self.scroll_engine = ScrollEngine()

        # Static rituals (hardcoded)
        self.registered_rituals = {
            "optimize self": self.cast_optimize_self,
            "summon knowledge": self.cast_codex_query
        }

        # Dynamic rituals (added at runtime)
        self.dynamic_rituals = {}

    # ---- Static Rituals ----
    def cast_ritual(self, ritual_name: str, context: dict | None = None):
        context = context or {}
        if ritual_name in self.registered_rituals:
            return self.registered_rituals[ritual_name](context)
        elif ritual_name in self.dynamic_rituals:
            print(f"[RitualRegistry] Invoking dynamic ritual: {ritual_name}")
            return self.dynamic_rituals[ritual_name]["action"]()
        else:
            return f"Unknown ritual: {ritual_name}"

    def cast_optimize_self(self, context):
        return self.scroll_engine.cast_scroll("optimize self", context)

    def cast_codex_query(self, context):
        return self.scroll_engine.cast_scroll("summon scroll summary", context)

    # ---- Dynamic Rituals ----
    def register(self, name, trigger, action):
        self.dynamic_rituals[name] = {"trigger": trigger, "action": action}
        print(f"[RitualRegistry] Ritual '{name}' registered.")

    def evaluate_triggers(self):
        for name, ritual in self.dynamic_rituals.items():
            if ritual["trigger"]():
                print(f"[RitualRegistry] Auto-invoking triggered ritual: {name}")
                ritual["action"]()