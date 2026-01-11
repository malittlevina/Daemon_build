from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Event:
    type: str
    payload: Any = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnimindContext:
    """
    Shared context object passed through Unimind modules.

    Provides:
    - a single mutable dict-like store (`data`)
    - an event log (`events`) for traceability
    """

    data: Dict[str, Any] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)

    def emit(self, event_type: str, payload: Any = None, **meta: Any) -> None:
        self.events.append(Event(type=event_type, payload=payload, meta=dict(meta)))

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

