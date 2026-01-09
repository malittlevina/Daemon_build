from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from storyrealms.events import RealmEvent


class SchemaError(ValueError):
    pass


Validator = Callable[[RealmEvent], None]


def _require_str(v: Any, name: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise SchemaError(f"{name} must be a non-empty string")
    return v


def _require_dict(v: Any, name: str) -> Dict[str, Any]:
    if not isinstance(v, dict):
        raise SchemaError(f"{name} must be a dict")
    return v


def validate_flag_set(ev: RealmEvent) -> None:
    p = _require_dict(ev.payload, "payload")
    _require_str(p.get("key"), "payload.key")


def validate_entity_upsert(ev: RealmEvent) -> None:
    p = _require_dict(ev.payload, "payload")
    _require_str(p.get("entity_id"), "payload.entity_id")
    data = p.get("data")
    if not isinstance(data, dict):
        raise SchemaError("payload.data must be a dict")


def validate_location_upsert(ev: RealmEvent) -> None:
    p = _require_dict(ev.payload, "payload")
    _require_str(p.get("location_id"), "payload.location_id")
    data = p.get("data")
    if not isinstance(data, dict):
        raise SchemaError("payload.data must be a dict")


def validate_scene_set(ev: RealmEvent) -> None:
    p = _require_dict(ev.payload, "payload")
    _require_str(p.get("scene"), "payload.scene")


def validate_relationship_adjust(ev: RealmEvent) -> None:
    p = _require_dict(ev.payload, "payload")
    _require_str(p.get("a"), "payload.a")
    _require_str(p.get("b"), "payload.b")
    try:
        float(p.get("delta"))
    except Exception:
        raise SchemaError("payload.delta must be numeric")


def validate_npc_goal_set(ev: RealmEvent) -> None:
    p = _require_dict(ev.payload, "payload")
    _require_str(p.get("entity_id"), "payload.entity_id")
    _require_str(p.get("goal"), "payload.goal")


DEFAULT_VALIDATORS: Dict[str, Validator] = {
    "flag.set": validate_flag_set,
    "entity.upsert": validate_entity_upsert,
    "location.upsert": validate_location_upsert,
    "scene.set": validate_scene_set,
    "relationship.adjust": validate_relationship_adjust,
    "npc.goal.set": validate_npc_goal_set,
}


@dataclass(slots=True)
class SchemaRegistry:
    validators: Dict[str, Validator]

    def validate(self, ev: RealmEvent) -> None:
        v = self.validators.get(ev.type)
        if v is None:
            return
        v(ev)

