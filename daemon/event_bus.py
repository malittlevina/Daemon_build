from __future__ import annotations

import queue
from dataclasses import dataclass
from typing import Optional

from daemon.events import DaemonEvent


@dataclass
class EventBus:
    """
    Minimal in-process event bus using a thread-safe queue.
    """

    maxsize: int = 1000

    def __post_init__(self) -> None:
        self._q: "queue.Queue[DaemonEvent]" = queue.Queue(maxsize=self.maxsize)

    def publish(self, event: DaemonEvent) -> None:
        try:
            self._q.put(event, block=False)
        except queue.Full:
            # Drop oldest by draining one, then try once.
            try:
                _ = self._q.get(block=False)
            except queue.Empty:
                pass
            try:
                self._q.put(event, block=False)
            except queue.Full:
                pass

    def get(self, timeout: Optional[float] = None) -> Optional[DaemonEvent]:
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

