from __future__ import annotations

from typing import Any

from unimind.context import UnimindContext


class LanguageNLUModule:
    """
    Language front-end: turns raw input into an interpreted result.
    """

    def __init__(self, nlu_engine):
        self.nlu = nlu_engine

    def process(self, user_input: str, context: UnimindContext) -> Any:
        # Prefer side-effect free planning when available.
        intent = None
        if hasattr(self.nlu, "plan"):
            try:
                intent = self.nlu.plan(user_input)
            except Exception:
                intent = None

        if intent:
            context.set("intent", intent)
            context.emit("intent_planned", intent, engine=self.nlu.__class__.__name__)
            return None

        # Fallback: legacy interpret (may be side-effectful).
        result = self.nlu.interpret(user_input)
        context.set("nlu_result", result)
        context.emit("nlu_result", result, engine=self.nlu.__class__.__name__)

        if isinstance(result, str) and result.startswith("[NLUEngine] No known intent"):
            return None
        return result

