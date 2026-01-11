from __future__ import annotations

from typing import Any, Dict, Optional


class EthicsGuardModule:
    """
    Ethics gate: can block actions based on policy signals.
    """

    def __init__(self, ethical_core):
        self.core = ethical_core

    def process(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        candidate = context.get("nlu_result", user_input)
        verdict = self.core.evaluate_action(str(candidate))
        context["ethics_verdict"] = verdict

        if isinstance(verdict, str) and verdict.lower().startswith("reject"):
            return f"[Daemon][Ethics] {verdict}"
        return None

