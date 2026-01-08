from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, DefaultDict
from collections import defaultdict

from .messages import KernelEvent

EventHandler = Callable[[KernelEvent], Any]


@dataclass(slots=True)
class Subscription:
    topic: str
    handler: EventHandler


class EventBus:
    """
    In-process pub/sub bus for kernel events.

    - Topic routing is prefix-based: publishing to `nlu.input` notifies handlers
      subscribed to `nlu.input` and `nlu` (and `*`).
    - Handlers should be side-effect safe; exceptions are contained.
    """

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: EventHandler) -> Subscription:
        self._subscribers[topic].append(handler)
        return Subscription(topic=topic, handler=handler)

    def unsubscribe(self, subscription: Subscription) -> None:
        handlers = self._subscribers.get(subscription.topic)
        if not handlers:
            return
        try:
            handlers.remove(subscription.handler)
        except ValueError:
            return

    def publish(self, topic: str, event: KernelEvent) -> None:
        # Topics to notify: exact, prefixes, wildcard.
        to_notify: list[EventHandler] = []
        to_notify.extend(self._subscribers.get("*", []))
        to_notify.extend(self._subscribers.get(topic, []))
        if "." in topic:
            parts = topic.split(".")
            for i in range(1, len(parts)):
                prefix = ".".join(parts[:i])
                to_notify.extend(self._subscribers.get(prefix, []))

        for handler in to_notify:
            try:
                handler(event)
            except Exception as e:  # pragma: no cover - containment by design
                # Avoid import-time coupling to logger subsystems.
                print(f"[KernelBus] Handler error for topic '{topic}': {e}")

