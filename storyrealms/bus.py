from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

from storyrealms.events import RealmEvent


Subscriber = Callable[[RealmEvent], None]


@dataclass(slots=True)
class EventBus:
    """
    In-process pub/sub for realm events.

    This is intentionally minimal; it provides a single place to hook integrations
    (scroll triggers, memory logging, UI bridges, etc.) without hard coupling.
    """

    subscribers: List[Subscriber] = field(default_factory=list)

    def subscribe(self, fn: Subscriber) -> None:
        if fn not in self.subscribers:
            self.subscribers.append(fn)

    def publish(self, event: RealmEvent) -> None:
        for fn in list(self.subscribers):
            try:
                fn(event)
            except Exception as e:
                # Keep the world engine deterministic and resilient:
                # subscriber failures should not break state transitions.
                print(f"[Storyrealms][EventBus] subscriber error: {e}")

