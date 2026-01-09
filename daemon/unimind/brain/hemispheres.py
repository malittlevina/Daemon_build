from __future__ import annotations

from typing import Any, Dict, List

from ..context import UnimindContext
from .types import ThoughtProposal


class LeftHemisphere:
    """
    Analytic/executive: prefers explicit protocols and deterministic next steps.
    """

    name = "left_hemisphere"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        attention = (state.get("attention") or {})
        text = (attention.get("input_text") or "").lower()

        lam_plan = (ctx.notes.get("subsystem_thoughts", {}) or {}).get("lam_plan")

        proposals: List[ThoughtProposal] = []
        if lam_plan:
            proposals.append(
                ThoughtProposal(
                    key="lh_lam",
                    action=str(lam_plan),
                    scores={"logic": 0.75, "memory": 0.15, "emotion": 0.05, "intuition": 0.05},
                    rationale="LAM suggested a direct next protocol; prioritize execution.",
                    tags=["lam", "protocol"],
                )
            )

        if "optimize" in text or "fix" in text:
            proposals.append(
                ThoughtProposal(
                    key="lh_optimize",
                    action="trigger:optimize self",
                    scores={"logic": 0.65, "memory": 0.2, "emotion": 0.05, "intuition": 0.1},
                    rationale="User signaled optimization intent; route toward optimization scrolls.",
                    tags=["optimize"],
                )
            )

        if "study" in text or "learn" in text:
            proposals.append(
                ThoughtProposal(
                    key="lh_study",
                    action="trigger:study topic",
                    scores={"logic": 0.55, "memory": 0.2, "emotion": 0.1, "intuition": 0.15},
                    rationale="User signaled learning intent; route toward study protocol.",
                    tags=["study"],
                )
            )

        if not proposals:
            proposals.append(
                ThoughtProposal(
                    key="lh_log_wait",
                    action="log_and_wait",
                    scores={"logic": 0.15, "memory": 0.6, "emotion": 0.1, "intuition": 0.15},
                    rationale="No clear directive; default to logging state and awaiting further input.",
                    tags=["default"],
                )
            )

        return {"proposals_left": proposals}


class RightHemisphere:
    """
    Associative/creative: uses the concept graph to suggest exploration and reframes.
    """

    name = "right_hemisphere"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        graph = (ctx.notes or {}).get("concept_graph") or {}
        nodes: List[str] = list(graph.get("nodes") or [])
        # Prefer non-seed nodes for exploration suggestions
        exploration_terms = [n for n in nodes if isinstance(n, str) and len(n) > 2][:12]

        proposals: List[ThoughtProposal] = []
        if exploration_terms:
            term = exploration_terms[1] if len(exploration_terms) > 1 else exploration_terms[0]
            proposals.append(
                ThoughtProposal(
                    key="rh_explore",
                    action=f"explore:{term}",
                    scores={"logic": 0.25, "memory": 0.25, "emotion": 0.2, "intuition": 0.3},
                    rationale="Concept graph surfaced related terms; explore to broaden context and options.",
                    tags=["explore", "concept_graph"],
                    metadata={"term": term, "terms": exploration_terms},
                )
            )

        # Creativity-safe default: reflect and connect.
        proposals.append(
            ThoughtProposal(
                key="rh_reflect",
                action="idle_reflect",
                scores={"logic": 0.2, "memory": 0.25, "emotion": 0.2, "intuition": 0.35},
                rationale="Default to reflection when exploration signals are weak.",
                tags=["reflect", "default"],
            )
        )

        return {"proposals_right": proposals}

