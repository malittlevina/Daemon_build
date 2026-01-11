from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def promote_to_long_term(
    item: Dict[str, Any],
    category: str = "general",
    out_dir: str = "memory_tree/long_term",
    ingest_observation=None,
) -> str:
    """
    Append a distilled/promoted memory item to long-term storage (JSONL).
    Optionally also ingest into Codex vector store via ingest_observation.
    """
    os.makedirs(out_dir, exist_ok=True)
    cat = "".join(c if c.isalnum() or c in "-_." else "_" for c in (category or "general"))[:64]
    path = os.path.join(out_dir, f"{cat}.jsonl")

    record = {"ts": _utc_iso(), "category": cat, "item": item}
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")

    if callable(ingest_observation):
        try:
            ingest_observation({"type": "memory.long_term", "category": cat, "item": item})
        except Exception:
            pass

    return path

