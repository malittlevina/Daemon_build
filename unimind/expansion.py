from __future__ import annotations

import re
from dataclasses import asdict
from typing import Any, Dict, List, Sequence, Set

from unimind.context import ConceptGraph
from unimind.knowledge import CodexIndex


def _keywords(text: str, max_terms: int = 8) -> List[str]:
    if not text:
        return []
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\\-]{2,}", text.lower())
    stop = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "from",
        "into",
        "your",
        "you",
        "are",
        "was",
        "were",
        "will",
        "can",
        "not",
        "but",
        "all",
        "any",
        "its",
        "our",
        "about",
        "everything",
        "know",
        "unimind",
    }
    uniq: List[str] = []
    seen: Set[str] = set()
    for t in tokens:
        if t in stop:
            continue
        if t not in seen:
            uniq.append(t)
            seen.add(t)
    return uniq[:max_terms]


def _memory_seeds(recent_memory_events: Sequence[Dict[str, Any]], max_terms: int = 6) -> List[str]:
    seeds: List[str] = []
    for e in recent_memory_events[-10:]:
        content = str(e.get("content") or "")
        for k in _keywords(content, max_terms=max_terms):
            seeds.append(k)
    # de-dup while preserving order
    out: List[str] = []
    seen: Set[str] = set()
    for s in seeds:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out[:max_terms]


class ConceptExpander:
    """
    Symbolic concept expansion that stitches together:
    - seed text keywords
    - recent memory keywords
    - lightweight local Codex snippet mining

    Output is a `ConceptGraph` (nodes + edges) suitable for later agent planning.
    """

    def __init__(self, codex_index: CodexIndex):
        self._codex = codex_index

    def expand(self, seed: str, recent_memory_events: Sequence[Dict[str, Any]] | None = None) -> ConceptGraph:
        recent_memory_events = recent_memory_events or []

        seed_terms = _keywords(seed, max_terms=8)
        mem_terms = _memory_seeds(recent_memory_events, max_terms=6)
        base_terms = [*seed_terms, *[t for t in mem_terms if t not in seed_terms]]

        nodes: List[str] = []
        edges: List[Dict[str, Any]] = []

        def add_node(n: str) -> None:
            if n and n not in nodes:
                nodes.append(n)

        add_node(seed)
        for t in base_terms:
            add_node(t)
            edges.append({"from": seed, "to": t, "type": "keyword"})

        # Codex-driven expansion: search each term, mine snippet terms, add "related" edges.
        related_terms: List[str] = []
        for t in base_terms[:6]:
            hits, snippets = self._codex.search_snippets(t, max_hits=5, window=2)
            mined = self._codex.top_terms_from_snippets(snippets, max_terms=10)
            for m in mined:
                if m == t:
                    continue
                related_terms.append(m)
                edges.append(
                    {
                        "from": t,
                        "to": m,
                        "type": "codex_related",
                        "evidence": [{"path": h.path, "line_no": h.line_no} for h in hits[:3]],
                    }
                )

        # De-dup related terms and add as nodes (cap to avoid unbounded graphs).
        seen: Set[str] = set(nodes)
        for r in related_terms:
            if r not in seen:
                nodes.append(r)
                seen.add(r)
            if len(nodes) >= 60:
                break

        return ConceptGraph(
            seed=seed,
            nodes=nodes,
            edges=edges[:200],
            metadata={
                "seed_terms": seed_terms,
                "memory_terms": mem_terms,
                "base_terms": base_terms,
            },
        )

    def explain(self, graph: ConceptGraph) -> Dict[str, Any]:
        """
        Human-readable summary structure (kept as dict for easy logging).
        """
        by_type: Dict[str, int] = {}
        for e in graph.edges:
            by_type[e.get("type", "unknown")] = by_type.get(e.get("type", "unknown"), 0) + 1
        return {"seed": graph.seed, "node_count": len(graph.nodes), "edge_types": by_type, "metadata": graph.metadata}
