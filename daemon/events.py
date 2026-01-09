from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional


EventType = Literal[
    "text_input",
    "audio_transcript",
    "vision_label",
    "system_event",
    "shutdown",
]


@dataclass(frozen=True)
class DaemonEvent:
    type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "payload": self.payload,
            "source": self.source,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
        }

