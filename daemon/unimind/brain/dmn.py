from __future__ import annotations

from typing import Any, Dict, List

from ..context import UnimindContext


class DefaultModeNetwork:
    """
    Offline reflection + narrative stitching.

    Produces a compact "insight" object that can be logged by Unimind.
    """

    name = "default_mode_network"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        # Only run DMN when explicitly reflecting or when no direct input is present.
        mode = (state.get("language_frame") or {}).get("mode")
        if ctx.input_text and mode not in {"reflect"}:
            return {"dmn": None}

        graph = (ctx.notes or {}).get("concept_graph") or {}
        nodes: List[str] = list(graph.get("nodes") or [])[:12]
        recalled = list(state.get("recalled_episodes") or [])[-3:]

        insight = {
            "summary": "Offline reflection: consolidating recent episodes and concepts.",
            "top_concepts": nodes,
            "recalled": recalled,
        }
        return {"dmn": insight}

