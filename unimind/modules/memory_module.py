from __future__ import annotations

import json
from typing import Any, Dict

from unimind.context import UnimindContext


class MemoryModule:
    """
    Records interactions to the daemon's memory logger.
    """

    def __init__(self, memory_logger):
        self.memory = memory_logger

    def process(self, user_input: str, context: UnimindContext) -> None:
        output = context.get("output")
        entry: Dict[str, Any] = {
            "input": user_input,
            "output": output,
            "emotion": context.get("emotion"),
            "ethics": context.get("ethics_verdict"),
            "events": [
                {"type": e.type, "meta": e.meta}
                for e in (context.events or [])
            ],
        }
        # Ensure it can be JSON-serialized (best-effort).
        try:
            json.dumps(entry)
        except Exception:
            entry["output"] = str(output)

        try:
            self.memory.log_event("interaction", entry, context={"subsystem": "unimind"})
        except Exception:
            pass
        return None

