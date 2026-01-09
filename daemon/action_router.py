from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional, Tuple

from codex.ingestion import ingest_observation
from unimind.context import UnimindPlan


class ActionRouter:
    """
    Executes Unimind plans by routing symbolic actions to subsystems.

    Keep this separate from the brain: the brain proposes/selects; the router executes.
    """

    def __init__(self, *, scroll_engine: Any = None):
        self._scrolls = scroll_engine

    def route(self, plan: UnimindPlan, trace: Dict[str, Any] | None = None) -> Dict[str, Any]:
        action = str(plan.action or "")
        trace = trace or {}

        # Default: log-only outcome
        outcome: Dict[str, Any] = {"action": action, "executed": False, "result": None}

        # Handle explicit triggers
        if action.startswith("trigger:"):
            name = action.split("trigger:", 1)[1].strip()
            if not self._scrolls:
                outcome.update({"executed": False, "result": "No ScrollEngine attached."})
                return outcome

            # Attempt parameterization from language frame
            frame = (trace.get("notes") or {}).get("language_frame") or {}
            topic = frame.get("topic")

            try:
                if name == "study topic":
                    result = self._scrolls.invoke(name, topic)
                else:
                    result = self._scrolls.invoke(name)
                outcome.update({"executed": True, "result": result})
            except Exception as e:
                outcome.update({"executed": False, "result": f"Scroll error: {e}"})
            return outcome

        # Exploration: log a Codex query request (actual codex search is dependency-fragmented in repo)
        if action.startswith("explore:"):
            term = action.split("explore:", 1)[1].strip()
            ingest_observation({"type": "explore", "term": term, "plan": asdict(plan)})
            outcome.update({"executed": True, "result": f"Logged explore request for: {term}"})
            return outcome

        # LAM strings are already the "action"; treat them as "executed" by acknowledgement.
        if action.startswith("[LAM]"):
            ingest_observation({"type": "lam_plan", "plan": asdict(plan)})
            outcome.update({"executed": True, "result": "LAM plan acknowledged/logged."})
            return outcome

        if action in {"idle_reflect", "log_and_wait"}:
            ingest_observation({"type": "idle", "action": action, "plan": asdict(plan)})
            outcome.update({"executed": True, "result": "Idle action logged."})
            return outcome

        ingest_observation({"type": "unrouted_action", "action": action, "plan": asdict(plan)})
        outcome.update({"executed": False, "result": "No route matched; action logged."})
        return outcome

