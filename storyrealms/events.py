from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_dict(value: Any, field_name: str) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    raise TypeError(f"{field_name} must be a dict, got {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class RealmEvent:
    """
    Immutable event envelope for realm state transitions.

    All realm changes should be representable as events for determinism + replay.
    """

    type: str
    realm: str
    payload: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)
    actor: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))
    ts: str = field(default_factory=_utc_now_iso)

    def __post_init__(self) -> None:
        if not isinstance(self.type, str) or not self.type.strip():
            raise ValueError("event type must be a non-empty string")
        if not isinstance(self.realm, str) or not self.realm.strip():
            raise ValueError("event realm must be a non-empty string")
        object.__setattr__(self, "payload", _require_dict(self.payload, "payload"))
        object.__setattr__(self, "meta", _require_dict(self.meta, "meta"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "ts": self.ts,
            "type": self.type,
            "realm": self.realm,
            "actor": self.actor,
            "payload": self.payload,
            "meta": self.meta,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "RealmEvent":
        return RealmEvent(
            id=str(data.get("id") or str(uuid4())),
            ts=str(data.get("ts") or _utc_now_iso()),
            type=str(data.get("type") or ""),
            realm=str(data.get("realm") or ""),
            actor=data.get("actor"),
            payload=_require_dict(data.get("payload"), "payload"),
            meta=_require_dict(data.get("meta"), "meta"),
        )

