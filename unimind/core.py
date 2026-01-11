from __future__ import annotations

from typing import Any, Dict, Optional


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

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        for logic_module in self.modules["logic"]:
            logic_module.think()

    def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Route a query through Unimind's subsystems with a shared context object.

        Pipeline order (agent-native): language → ethics → logic → emotion → memory.
        Each module may:
        - enrich `context`
        - return an output (the latest non-None output is treated as the response)
        """
        ctx: Dict[str, Any] = dict(context or {})
        ctx["input"] = user_input

        output: Any = None
        for module_type in ("language", "ethics", "logic", "emotion", "memory"):
            for module in self.modules.get(module_type, []):
                try:
                    if hasattr(module, "process"):
                        candidate = module.process(user_input, ctx)
                        if candidate is not None:
                            output = candidate
                            ctx["output"] = output
                except Exception as e:
                    ctx.setdefault("errors", []).append({"module_type": module_type, "error": str(e)})

        return output if output is not None else "[Unimind] No response."
