from __future__ import annotations

from typing import Any, Dict

from ..context import UnimindContext


class ExecutiveScheduler:
    """
    Meta-controller / executive scheduler.

    Chooses how much cognition to run (fast vs deep) and sets budgets.
    """

    name = "executive_scheduler"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        intero = state.get("interoception") or {}
        load = float(intero.get("load", 0.2) or 0.2)

        sal = (state.get("salience") or {})
        salience = float((sal.get("salience") or 0.0))

        conflict = state.get("conflict_monitor") or {}
        conflict_score = float(conflict.get("conflict_score", 0.0) or 0.0)

        # Defaults
        mode = "deep"
        budget = {"max_proposals": 6, "max_concept_nodes": 25}

        # High load => fast path, unless high salience or conflict requires deep review.
        if load > 0.7 and salience < 0.6 and conflict_score < 0.6:
            mode = "fast"
            budget = {"max_proposals": 3, "max_concept_nodes": 12}

        # High threat/conflict => deep + ethics pressure
        if salience >= 0.7 or conflict_score >= 0.7:
            mode = "deep"
            budget = {"max_proposals": 6, "max_concept_nodes": 25}

        return {"scheduler": {"mode": mode, "budget": budget, "load": load, "salience": salience, "conflict": conflict_score}}

