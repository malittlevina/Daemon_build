from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from devices.types import DevicePassport


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class DeviceEvent:
    """
    Event emitted by discovery/integration layers.
    """

    kind: str  # device.discovered | device.updated | device.lost | device.pairing_required | device.ready
    passport: DevicePassport
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "timestamp": self.timestamp,
            "passport": self.passport.to_dict(),
            "data": self.data,
        }

