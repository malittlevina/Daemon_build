from __future__ import annotations

import re
from typing import Any, Dict, Optional

from unimind.context import UnimindContext


class WernickeArea:
    """
    Language understanding: normalize input + intent into a lightweight semantic frame.
    """

    name = "wernicke"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        text = (ctx.input_text or "").strip()
        intent = ctx.intent

        frame: Dict[str, Any] = {"raw": text, "intent": intent}
        lower = text.lower()
        if "optimize" in lower:
            frame["mode"] = "optimize"
        elif "study" in lower or "learn" in lower:
            frame["mode"] = "learn"
        elif "reflect" in lower:
            frame["mode"] = "reflect"
        else:
            frame["mode"] = "unknown"

        # Extract a naive "topic" after keywords (best-effort)
        m = re.search(r"(study|learn)\s+(.+)$", lower)
        if m:
            frame["topic"] = m.group(2).strip()[:80]

        return {"language_frame": frame}


class BrocaArea:
    """
    Language generation planning: produce a structured response template
    to accompany the selected plan.
    """

    name = "broca"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        plan = state.get("plan")
        if plan is None:
            return {"utterance_plan": {"text": "I’m reflecting and waiting for more input."}}

        action = getattr(plan, "action", "")
        rationale = getattr(plan, "rationale", "")
        question = (state.get("conflict_monitor") or {}).get("clarifying_question")

        if question:
            text = f"[Unimind] I detected conflicting signals. {question}"
        else:
            text = f"[Unimind] Next: {action}\n[Unimind] Why: {rationale}"

        return {"utterance_plan": {"text": text, "action": action}}

