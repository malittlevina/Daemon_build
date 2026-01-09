from __future__ import annotations

from typing import Any, Dict, List, Tuple

from unimind.context import UnimindContext
from unimind.brain.types import ThoughtProposal


class CorpusCallosum:
    """
    Integrator: merges left/right hemisphere proposals, de-duplicates, and
    records conflicts.
    """

    name = "corpus_callosum"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        left: List[ThoughtProposal] = list(state.get("proposals_left") or [])
        right: List[ThoughtProposal] = list(state.get("proposals_right") or [])

        proposals: List[ThoughtProposal] = []
        seen_actions = set()
        conflicts: List[Tuple[str, str]] = []

        for p in left + right:
            a = p.action.strip()
            if a in seen_actions:
                continue
            # basic conflict heuristic: "log_and_wait" conflicts with direct triggers
            if a == "log_and_wait" and any(x.action.startswith(("trigger:", "explore:")) for x in proposals):
                conflicts.append(("log_and_wait", "active_intent"))
                continue
            proposals.append(p)
            seen_actions.add(a)

        # Cap proposals for stability
        proposals = proposals[:8]

        return {"proposals": proposals, "conflicts": conflicts}

