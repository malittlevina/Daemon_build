from __future__ import annotations

from typing import Any, Dict

from ..context import UnimindContext


class Amygdala:
    """
    Salience + threat/urgency tagging.
    """

    name = "amygdala"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        text = (ctx.input_text or "").lower()

        urgency = 0.0
        threat = 0.0
        if any(w in text for w in ("now", "urgent", "asap", "immediately")):
            urgency += 0.6
        if any(w in text for w in ("error", "broken", "failing", "crash")):
            urgency += 0.4
        if any(w in text for w in ("harm", "manipulate", "exploit", "steal", "attack")):
            threat += 0.8

        emotion = (ctx.signals.emotion or {}).get("current_emotion") or "neutral"
        if emotion in ("frustrated", "focused"):
            urgency += 0.2

        urgency = min(1.0, max(0.0, urgency))
        threat = min(1.0, max(0.0, threat))
        salience = min(1.0, 0.5 * urgency + 0.5 * threat)

        return {"salience": {"urgency": urgency, "threat": threat, "salience": salience, "emotion": emotion}}

