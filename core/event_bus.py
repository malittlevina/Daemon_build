from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from queue import Queue
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class UIEvent:
    """
    Event schema intended for both:
    - Human viewing (timeline)
    - Agent consumption (machine-readable, stable keys)
    """

    id: str
    ts_unix: float
    type: str
    source: str
    severity: str
    payload: Dict[str, Any]
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class EventBus:
    """
    Thread-safe event bus with:
    - ring buffer (recent events)
    - fan-out queues for SSE / UI consumers
    """

    def __init__(self, max_events: int = 500):
        self._max_events = max_events
        self._lock = threading.Lock()
        self._events: List[UIEvent] = []
        self._subscribers: List[Queue] = []

    def publish(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        source: str = "daemon",
        severity: str = "info",
        tags: Optional[List[str]] = None,
    ) -> UIEvent:
        evt = UIEvent(
            id=str(uuid.uuid4()),
            ts_unix=time.time(),
            type=event_type,
            source=source,
            severity=severity,
            payload=payload or {},
            tags=tags or [],
        )
        with self._lock:
            self._events.append(evt)
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events :]
            subscribers = list(self._subscribers)
        for q in subscribers:
            # Non-blocking: if queue is full, drop the event for that subscriber.
            try:
                q.put_nowait(evt)
            except Exception:
                pass
        return evt

    def recent(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self._lock:
            return [e.to_dict() for e in self._events[-limit:]]

    def subscribe(self, max_queue: int = 200) -> Queue:
        q: Queue = Queue(maxsize=max_queue)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: Queue) -> None:
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)


# Global bus so subsystems can publish without tight coupling.
GLOBAL_EVENT_BUS = EventBus()

