from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class KernelEvent:
    """
    A minimal, typed message exchanged across subsystems.

    Events are intentionally generic: the kernel does not assume any one
    subsystem's schema, only that events can be routed and observed.
    """

    type: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

