from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence

from unimind.context import UnimindContext


class Hippocampus:
    """
    Episodic consolidation + recall gating.

    - Builds lightweight "episodes" from recent memory events.
    - Produces a small set of recalled episodes relevant to the current input.
    """

    name = "hippocampus"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        recent_events: Sequence[Dict[str, Any]] = (ctx.signals.memory or {}).get("recent_events", []) or []
        text = (ctx.input_text or "").lower()
        tokens = set(re.findall(r"[a-z][a-z0-9_\\-]{2,}", text)) if text else set()

        episodes: List[Dict[str, Any]] = []
        for e in recent_events[-20:]:
            content = str(e.get("content") or "")
            etype = str(e.get("type") or "")
            episodes.append(
                {
                    "type": etype,
                    "content": content[:400],
                    "timestamp": e.get("timestamp"),
                }
            )

        recalled: List[Dict[str, Any]] = []
        if tokens:
            for ep in episodes:
                c = ep["content"].lower()
                if any(t in c for t in list(tokens)[:10]):
                    recalled.append(ep)
        else:
            recalled = episodes[-5:]

        recalled = recalled[-5:]
        return {"episodes": episodes[-20:], "recalled_episodes": recalled}

