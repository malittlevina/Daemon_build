from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional


AvatarEventType = Literal[
    "state",          # idle/listening/thinking/speaking/executing/error
    "expression",     # set facial expression
    "gesture",        # nod/shake/wave/point/etc
    "look_at",        # look direction/target
    "speak",          # text + optional timing
    "debug",          # dev telemetry
]


@dataclass(frozen=True)
class AvatarEvent:
    type: AvatarEventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    source: str = "daemon"
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "type": self.type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
        }
        if self.id:
            d["id"] = self.id
        return d

