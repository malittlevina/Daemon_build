from __future__ import annotations

from typing import Any, Dict, Optional

from unimind.context import UnimindContext


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
        ctx_obj = UnimindContext(data=dict(context or {}))
        ctx_obj.set("input", user_input)
        ctx_obj.emit("input_received", {"input": user_input})

        output: Any = None
        for module_type in ("language", "ethics", "logic", "emotion", "memory"):
            for module in self.modules.get(module_type, []):
                try:
                    if hasattr(module, "process"):
                        ctx_obj.emit("module_enter", {"module_type": module_type, "module": module.__class__.__name__})
                        candidate = module.process(user_input, ctx_obj)
                        if candidate is not None:
                            output = candidate
                            ctx_obj.set("output", output)
                            ctx_obj.emit("module_output", {"module_type": module_type}, output_type=type(output).__name__)
                except Exception as e:
                    errors = ctx_obj.get("errors", [])
                    errors.append({"module_type": module_type, "error": str(e), "module": module.__class__.__name__})
                    ctx_obj.set("errors", errors)
                    ctx_obj.emit("module_error", {"module_type": module_type, "error": str(e)})

        ctx_obj.emit("response_ready", {"has_output": output is not None})
        return output if output is not None else "[Unimind] No response."
