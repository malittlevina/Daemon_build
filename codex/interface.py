from __future__ import annotations

import json
import os
from typing import Any, Dict, List


class CodexInterface:
    """
    Lightweight compatibility layer for components expecting `codex.interface.CodexInterface`.

    Today it reads from existing daemon logs/memory rather than a dedicated Codex DB.
    """

    def __init__(self, memory_log_path: str = "memory_tree/logs/memory_log.json"):
        self.memory_log_path = memory_log_path

    def get_recent_logs(self, limit: int = 10) -> List[str]:
        limit_i = max(1, int(limit))

        if os.path.exists(self.memory_log_path):
            try:
                with open(self.memory_log_path, "r") as f:
                    data = json.load(f)
                # Each entry is a dict; stringify for SelfReflector analysis.
                return [json.dumps(e, default=str) for e in (data or [])[-limit_i:]]
            except Exception:
                pass

        # Fallback: read from improvement history if present
        alt = "logs/improvement_history.log"
        if os.path.exists(alt):
            try:
                with open(alt, "r") as f:
                    lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                return lines[-limit_i:]
            except Exception:
                pass

        return []

