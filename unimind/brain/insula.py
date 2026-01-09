from __future__ import annotations

from typing import Any, Dict, Sequence

from unimind.context import UnimindContext


class Insula:
    """
    Interoception / system health monitor.

    Uses recent memory events as a proxy for "system load" and "error rate".
    """

    name = "insula"

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        recent: Sequence[Dict[str, Any]] = (ctx.signals.memory or {}).get("recent_events", []) or []
        if not recent:
            return {"interoception": {"load": 0.1, "error_rate": 0.0, "notes": "no_recent_events"}}

        errors = 0
        total = 0
        for e in recent[-25:]:
            total += 1
            content = str(e.get("content") or "").lower()
            etype = str(e.get("type") or "").lower()
            if "error" in content or "exception" in content or "critical" in content or etype in {"error", "exception"}:
                errors += 1

        error_rate = (errors / total) if total else 0.0
        # load is a soft proxy: more recent events + more errors => higher load
        load = min(1.0, 0.2 + 0.6 * error_rate + 0.2 * min(1.0, total / 25))
        return {"interoception": {"load": load, "error_rate": error_rate, "recent_events": total}}

