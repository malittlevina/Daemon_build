from __future__ import annotations

import re
from typing import Any, Dict, List

from ..context import UnimindContext


class Thalamus:
    """
    Attention gateway: compresses the full context into a small "attention packet"
    for downstream reasoning.
    """

    name = "thalamus"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        text = (ctx.input_text or "").strip()
        emotion = (ctx.signals.emotion or {}).get("current_emotion")
        recent_events = (ctx.signals.memory or {}).get("recent_events", []) or []
        graph = (ctx.notes or {}).get("concept_graph") or {}
        recall = (ctx.notes or {}).get("knowledge_recall") or []

        tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\\-]{2,}", text.lower()) if text else []
        top_tokens: List[str] = []
        seen = set()
        for t in tokens:
            if t in seen:
                continue
            top_tokens.append(t)
            seen.add(t)
            if len(top_tokens) >= 8:
                break

        recall_summaries: List[Dict[str, Any]] = []
        if isinstance(recall, list):
            for a in recall[:5]:
                if not isinstance(a, dict):
                    continue
                recall_summaries.append(
                    {
                        "id": a.get("id"),
                        "kind": a.get("kind"),
                        "title": a.get("title") or a.get("name") or a.get("goal"),
                        "definition": (a.get("definition") or a.get("description") or "")[:200],
                        "tags": (a.get("tags") or [])[:8],
                    }
                )

        attention = {
            "input_text": text,
            "tokens": top_tokens,
            "emotion": emotion,
            "recent_memory_count": len(recent_events),
            "concept_nodes": (graph.get("nodes") or [])[:25],
            "knowledge": recall_summaries,
        }
        return {"attention": attention}

