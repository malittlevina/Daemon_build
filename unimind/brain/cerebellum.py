from __future__ import annotations

from typing import Any, Dict

from unimind.context import UnimindContext


class Cerebellum:
    """
    Skill refinement + timing.

    Without an execution/outcome loop in this repo, we implement a minimal
    refinement mechanism:
    - track action frequencies
    - track "error-associated" cycles from memory/insula
    """

    name = "cerebellum"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        memory: Dict[str, Any] = state.setdefault("_brain_memory", {})
        stats: Dict[str, Any] = memory.setdefault("cerebellum_stats", {"actions": {}, "error_cycles": 0, "cycles": 0})

        stats["cycles"] = int(stats.get("cycles", 0)) + 1

        plan = state.get("plan")
        if plan is not None:
            action = str(getattr(plan, "action", "") or "")
            stats["actions"][action] = int(stats["actions"].get(action, 0)) + 1

        intero = state.get("interoception") or {}
        if float(intero.get("error_rate", 0.0) or 0.0) > 0.2:
            stats["error_cycles"] = int(stats.get("error_cycles", 0)) + 1

        return {"refinement": {"cerebellum_stats": stats}}

