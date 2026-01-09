from __future__ import annotations

from typing import Callable, Optional

from storyrealms.events import RealmEvent


def memory_logger_sink(event: RealmEvent) -> None:
    """
    Soft integration: write realm events into the daemon's memory stream.

    Uses global helper `memory_tree.memory_logger.log_memory` if present.
    """
    try:
        from memory_tree.memory_logger import log_memory  # type: ignore
    except Exception:
        return

    content = f"[Storyrealms] {event.realm} :: {event.type}"
    context = {
        "event_id": event.id,
        "ts": event.ts,
        "realm": event.realm,
        "type": event.type,
        "actor": event.actor,
        "payload": event.payload,
        "meta": event.meta,
    }
    try:
        log_memory(content, context=context)
    except Exception:
        return


def scroll_trigger_sink(event: RealmEvent) -> None:
    """
    Soft integration: allow realm events to invoke scrolls.

    Convention:
    - event.type == "scroll.trigger"
    - payload: {"name": <scroll_name>, "reason": <optional>}
    """
    if event.type != "scroll.trigger":
        return
    name = (event.payload or {}).get("name")
    if not isinstance(name, str) or not name.strip():
        return

    reason = (event.payload or {}).get("reason") or "storyrealms"
    try:
        from scrolls.trigger_manager import trigger_scroll  # type: ignore
    except Exception:
        return

    try:
        trigger_scroll(name, reason=reason)
    except Exception:
        return


def compose_sinks(*sinks: Callable[[RealmEvent], None]) -> Callable[[RealmEvent], None]:
    def _sink(event: RealmEvent) -> None:
        for fn in sinks:
            fn(event)
    return _sink

