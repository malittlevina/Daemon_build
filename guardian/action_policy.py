from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PolicyVerdict:
    ok: bool
    reason: str = ""


class ActionPolicy:
    """
    Lightweight allowlist-based action safety policy.

    This is intentionally conservative and offline.
    """

    def __init__(self):
        self.allowed_intents = {
            "xr.list_apps",
            "xr.create_world",
            "xr.train_sim",
            # Launch is allowed only as dry-run by default.
            "xr.launch_app",
            "memory.sort_day",
            "memory.garden",
            "garden.status",
            "garden.open",
            "garden.plots",
            "garden.walk",
            "garden.seeds",
            "garden.inspect",
            "garden.tag",
            "garden.promote",
        }

    def evaluate(self, intent: Optional[Dict[str, Any]]) -> PolicyVerdict:
        if not intent:
            return PolicyVerdict(ok=True)
        name = str(intent.get("intent", "")).strip()
        if name and name not in self.allowed_intents:
            return PolicyVerdict(ok=False, reason=f"Intent not allowlisted: {name}")

        if name == "xr.launch_app":
            if not bool(intent.get("dry_run", True)):
                return PolicyVerdict(ok=False, reason="Blocking non-dry-run XR app launch.")

        return PolicyVerdict(ok=True)

