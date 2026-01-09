from __future__ import annotations

from typing import Any, Dict, List, Optional

from unimind.context import UnimindContext
from unimind.brain.types import ThoughtProposal


class BasalGanglia:
    """
    Habit / policy selector.

    Maintains a small policy table in persistent brain memory:
    - observation_key -> preferred proposal key
    """

    name = "basal_ganglia"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        memory: Dict[str, Any] = state.setdefault("_brain_memory", {})
        policy: Dict[str, str] = memory.setdefault("policy", {})

        language_frame = state.get("language_frame") or {}
        mode = language_frame.get("mode") or "unknown"
        key = f"mode:{mode}"

        proposals: List[ThoughtProposal] = list(state.get("proposals") or [])
        preferred_key = policy.get(key)

        bias: Dict[str, float] = {"logic": 0.0, "memory": 0.0, "emotion": 0.0, "intuition": 0.0}
        fast_path = None

        if preferred_key and any(p.key == preferred_key for p in proposals):
            # Boost the preferred proposal (fast, habitual response).
            bias["logic"] += 0.15
            bias["memory"] += 0.10
            fast_path = {"preferred_key": preferred_key, "reason": f"habit_policy_hit:{key}"}
        else:
            # If there's an obvious mapping, learn it.
            # (This is a conservative, rule-based "habit formation".)
            if mode == "optimize":
                candidate = next((p for p in proposals if "optimize" in p.key or "optimize" in p.action), None)
                if candidate:
                    policy[key] = candidate.key
            elif mode == "learn":
                candidate = next((p for p in proposals if "study" in p.key or "study" in p.action), None)
                if candidate:
                    policy[key] = candidate.key

        return {"policy_bias": bias, "habit": {"key": key, "preferred": policy.get(key), "fast_path": fast_path}}

