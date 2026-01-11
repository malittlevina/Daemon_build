from __future__ import annotations

from typing import Any, Optional

from unimind.context import UnimindContext
from guardian.action_policy import ActionPolicy


class EthicsGuardModule:
    """
    Ethics gate: can block actions based on policy signals.
    """

    def __init__(self, ethical_core):
        self.core = ethical_core
        self.policy = ActionPolicy()

    def process(self, user_input: str, context: UnimindContext) -> Optional[str]:
        intent = context.get("intent")
        pv = self.policy.evaluate(intent if isinstance(intent, dict) else None)
        context.set("policy_verdict", {"ok": pv.ok, "reason": pv.reason})
        context.emit("policy_verdict", {"ok": pv.ok, "reason": pv.reason})

        if not pv.ok:
            return f"[Daemon][Safety] Reject: {pv.reason}"

        candidate = context.get("nlu_result", user_input)
        verdict = self.core.evaluate_action(str(candidate))
        context.set("ethics_verdict", verdict)
        context.emit("ethics_verdict", verdict)

        if isinstance(verdict, str) and verdict.lower().startswith("reject"):
            return f"[Daemon][Ethics] {verdict}"
        return None

