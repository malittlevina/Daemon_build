from __future__ import annotations

from typing import Optional


def summarize_content(topic: str, max_chars: int = 1200) -> str:
    """
    Lightweight summarizer stub.

    In this repo, we keep summarization dependency-free and deterministic.
    If a richer model is available, it can be swapped in behind this API.
    """
    t = (topic or "").strip()
    if not t:
        return "[Codex] No topic provided."

    # Minimal heuristic summary template (agent-friendly).
    summary = (
        f"{t}:\n"
        f"- Definition: (add a concise definition)\n"
        f"- Key concepts: (list 3-7)\n"
        f"- Common pitfalls: (list 2-5)\n"
        f"- Practical checklist: (steps you would run in a real system)\n"
        f"- References: (URLs, docs, papers)\n"
    )
    return summary[:max_chars]

