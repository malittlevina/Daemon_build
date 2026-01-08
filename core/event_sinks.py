from __future__ import annotations

import os
import threading
import time
from typing import Optional

from core.event_bus import EventBus, UIEvent


def start_jsonl_event_sink(
    event_bus: EventBus,
    *,
    path: str = "logs/agent_ui_events.jsonl",
    include_recent: bool = True,
    flush_interval_sec: float = 1.0,
) -> threading.Thread:
    """
    Persist events to JSONL for debugging/replay/training.

    - Appends one event JSON per line.
    - Designed to be safe for long-running daemons.
    """

    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)

    q = event_bus.subscribe(max_queue=500)

    def _run() -> None:
        # Small delay to allow early publishers to start up.
        time.sleep(0.05)
        with open(path, "a", encoding="utf-8") as f:
            if include_recent:
                for evt in event_bus.recent(limit=50):
                    f.write(__import__("json").dumps(evt, ensure_ascii=False) + "\n")
                f.flush()

            last_flush = time.time()
            while True:
                evt: UIEvent = q.get()
                f.write(evt.to_json() + "\n")
                now = time.time()
                if now - last_flush >= flush_interval_sec:
                    f.flush()
                    last_flush = now

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t

