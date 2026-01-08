from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from queue import Queue
from threading import Lock
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Message:
    id: str
    ts_unix: float
    topic: str
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None


class MessageBus:
    """
    Simple in-process IPC for kernel services.
    - topic-based fanout
    - bounded queues (backpressure by drop)
    """

    def __init__(self):
        self._lock = Lock()
        self._subs: Dict[str, List[Queue]] = {}

    def publish(self, topic: str, payload: Optional[Dict[str, Any]] = None, *, source: str = "kernel", trace_id: Optional[str] = None) -> Message:
        msg = Message(
            id=str(uuid.uuid4()),
            ts_unix=time.time(),
            topic=topic,
            source=source,
            payload=payload or {},
            trace_id=trace_id,
        )
        with self._lock:
            queues = list(self._subs.get(topic, [])) + list(self._subs.get("*", []))
        for q in queues:
            try:
                q.put_nowait(msg)
            except Exception:
                # drop for that subscriber
                pass
        return msg

    def subscribe(self, topic: str, *, max_queue: int = 200) -> Queue:
        q: Queue = Queue(maxsize=max_queue)
        with self._lock:
            self._subs.setdefault(topic, []).append(q)
        return q

    def unsubscribe(self, topic: str, q: Queue) -> None:
        with self._lock:
            if topic in self._subs and q in self._subs[topic]:
                self._subs[topic].remove(q)

