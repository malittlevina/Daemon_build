from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..context import UnimindContext


class AnteriorCingulateCortex:
    """
    Conflict monitor: detects contradictions and raises "need-clarification"
    or "ethics-review" pressure.
    """

    name = "anterior_cingulate_cortex"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        conflicts: List[Any] = list(state.get("conflicts") or [])
        proposals = list(state.get("proposals") or [])

        ethics_pressure = 0.0
        # If user text contains risky words, request stronger review.
        text = (ctx.input_text or "").lower()
        if any(w in text for w in ("harm", "manipulate", "exploit", "steal", "attack")):
            ethics_pressure = 1.0

        conflict_score = 0.0
        if conflicts:
            conflict_score += 0.5
        if len(proposals) >= 5:
            conflict_score += 0.2
        sal = state.get("salience") or {}
        threat = float(sal.get("threat", 0.0) or 0.0)
        conflict_score = min(1.0, conflict_score + 0.3 * threat)

        needs_clarification = conflict_score >= 0.7
        if needs_clarification:
            # Provide a structured fallback question.
            question = "What outcome do you want (optimize, study, run a task, or reflect)?"
        else:
            question = None

        return {
            "conflict_monitor": {
                "conflict_score": conflict_score,
                "ethics_pressure": ethics_pressure,
                "needs_clarification": needs_clarification,
                "clarifying_question": question,
            }
        }

