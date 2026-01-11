from __future__ import annotations

from typing import Any, Dict, Optional


class ScrollRouterModule:
    """
    Logic/action router: maps common patterns to ScrollEngine invocations.

    This ensures non-XR actions still travel through the same Unimind pipeline.
    """

    def __init__(self, scroll_engine):
        self.scrolls = scroll_engine

    def process(self, user_input: str, context: Dict[str, Any]) -> Optional[Any]:
        text = (user_input or "").strip()
        text_l = text.lower()

        # If NLU already produced a non-trivial result, don't override it.
        nlu_result = context.get("nlu_result")
        if nlu_result is not None and not (
            isinstance(nlu_result, str) and nlu_result.startswith("[NLUEngine] No known intent")
        ):
            return None

        if text_l == "optimize self":
            return self.scrolls.invoke("optimize self")

        if text_l.startswith("run task "):
            desc = text[9:].strip()
            return self.scrolls.invoke("run task", desc)

        if text_l.startswith("multi step plan "):
            goal = text[len("multi step plan ") :].strip()
            return self.scrolls.invoke("multi step plan", goal)

        if text_l.startswith("study topic "):
            topic = text[len("study topic ") :].strip()
            return self.scrolls.invoke("study topic", topic)

        if text_l.startswith("study "):
            topic = text[len("study ") :].strip()
            return self.scrolls.invoke("study topic", topic)

        return None

