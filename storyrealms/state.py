from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class RealmState:
    """
    Canonical realm state snapshot.

    Keep this small and structural. High-frequency narrative detail should live in
    entities/locations/flags as data rather than new top-level fields.
    """

    realm: str
    schema_version: int = 1
    time: int = 0  # discrete ticks
    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    locations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relationships: Dict[str, Any] = field(default_factory=dict)
    flags: Dict[str, Any] = field(default_factory=dict)
    current_scene: Optional[str] = None
    last_event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "realm": self.realm,
            "time": self.time,
            "entities": self.entities,
            "locations": self.locations,
            "relationships": self.relationships,
            "flags": self.flags,
            "current_scene": self.current_scene,
            "last_event_id": self.last_event_id,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "RealmState":
        realm = str(data.get("realm") or "default")
        state = RealmState(
            realm=realm,
            schema_version=int(data.get("schema_version") or 1),
            time=int(data.get("time") or 0),
            entities=dict(data.get("entities") or {}),
            locations=dict(data.get("locations") or {}),
            relationships=dict(data.get("relationships") or {}),
            flags=dict(data.get("flags") or {}),
            current_scene=data.get("current_scene"),
            last_event_id=data.get("last_event_id"),
        )
        return state

