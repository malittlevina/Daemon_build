from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from unimind.context import UnimindContext, UnimindPlan
from unimind.decision_matrix import DecisionMatrix
from unimind.subsystems import EthicsSubsystem
from unimind.brain.types import ThoughtProposal


class PrefrontalCortex:
    """
    Executive selection: evaluates proposals, applies ethics review, emits plan.
    """

    name = "prefrontal_cortex"

    def __init__(self, decision: DecisionMatrix, ethics: Optional[EthicsSubsystem] = None):
        self._decision = decision
        self._ethics = ethics

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        proposals: List[ThoughtProposal] = list(state.get("proposals") or [])

        # Build options in the format expected by DecisionMatrix
        options: Dict[str, Dict[str, float]] = {p.key: dict(p.scores) for p in proposals}
        best_key, scored = self._decision.choose_with_rationale(options)
        selected = next((p for p in proposals if p.key == best_key), proposals[0] if proposals else None)

        if selected is None:
            plan = UnimindPlan(action="idle_reflect", rationale="No proposals available; default to reflection.", score=0.0)
            return {"plan": plan, "selected": None, "scored": scored}

        ethics_note = self._ethics.evaluate(selected.action) if self._ethics else None

        rationale = f"{selected.rationale} | Score: {scored[best_key]['rationale']}"
        if ethics_note:
            rationale = f"{rationale} | Ethics: {ethics_note}"

        plan = UnimindPlan(
            action=selected.action,
            rationale=rationale,
            score=float(scored[best_key]["score"]),
            details={
                "selected_key": best_key,
                "selected": asdict(selected),
                "scoring": scored,
                "ethics": ethics_note,
            },
        )
        return {"plan": plan, "selected": asdict(selected), "scored": scored}

