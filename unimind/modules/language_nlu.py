from __future__ import annotations

from typing import Any, Dict


class LanguageNLUModule:
    """
    Language front-end: turns raw input into an interpreted result.
    """

    def __init__(self, nlu_engine):
        self.nlu = nlu_engine

    def process(self, user_input: str, context: Dict[str, Any]) -> Any:
        result = self.nlu.interpret(user_input)
        context["nlu_result"] = result

        # If NLU has no idea, let downstream modules attempt routing.
        if isinstance(result, str) and result.startswith("[NLUEngine] No known intent"):
            return None

        return result

