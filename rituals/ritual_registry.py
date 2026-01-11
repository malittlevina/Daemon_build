# rituals/ritual_registry.py

from daemon.runtime import build_daemon_runtime
from scrolls.scroll_engine import ScrollEngine

class RitualRegistry:
    def __init__(self):
        self.runtime = build_daemon_runtime(use_ollama_fallback=False)
        self.scroll_engine = self.runtime.scrolls

        # Static rituals (hardcoded)
        self.registered_rituals = {
            "optimize self": self.cast_optimize_self,
            "summon knowledge": self.cast_codex_query,
            # XR rituals (voice-friendly)
            "xr list apps": self.cast_xr_list_apps,
        }

        # Dynamic rituals (added at runtime)
        self.dynamic_rituals = {}

    # ---- Static Rituals ----
    def cast_ritual(self, ritual_name: str, context: dict = {}):
        ritual = (ritual_name or "").strip().lower()

        # Allow voice commands like: "xr train sim practice teleport comfort"
        if ritual.startswith("xr "):
            return self.runtime.unimind.process_input(ritual, context={"source": "voice"})

        if ritual in self.registered_rituals:
            return self.registered_rituals[ritual](context)
        elif ritual in self.dynamic_rituals:
            print(f"[RitualRegistry] Invoking dynamic ritual: {ritual}")
            return self.dynamic_rituals[ritual]["action"]()
        else:
            # Voice fallback: let NLU attempt routing (without Ollama).
            return self.runtime.unimind.process_input(ritual, context={"source": "voice"})

    def cast_optimize_self(self, context):
        return self.scroll_engine.invoke("optimize self")

    def cast_codex_query(self, context):
        # Keep this safe even if Codex indexing isn't configured.
        query = ""
        if isinstance(context, dict):
            query = str(context.get("query", "")).strip()
        return f"[RitualRegistry] Knowledge query received: {query or '(none)'}"

    def cast_xr_list_apps(self, context):
        return self.scroll_engine.invoke("xr list apps")

    # ---- Dynamic Rituals ----
    def register(self, name, trigger, action):
        self.dynamic_rituals[name] = {"trigger": trigger, "action": action}
        print(f"[RitualRegistry] Ritual '{name}' registered.")

    def evaluate_triggers(self):
        for name, ritual in self.dynamic_rituals.items():
            if ritual["trigger"]():
                print(f"[RitualRegistry] Auto-invoking triggered ritual: {name}")
                ritual["action"]()