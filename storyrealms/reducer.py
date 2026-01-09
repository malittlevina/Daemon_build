from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from storyrealms.events import RealmEvent
from storyrealms.state import RealmState


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal deep merge for nested dicts.
    - dict values are merged recursively
    - other values overwrite
    """
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            dst[k] = _deep_merge(dst[k], v)  # type: ignore[index]
        else:
            dst[k] = v
    return dst


def apply_event(state: RealmState, event: RealmEvent) -> RealmState:
    """
    Deterministic state transition function.

    All state changes should happen here (or through reducers called here).
    """
    if event.realm != state.realm:
        # Service will ensure correct realm routing; reducer stays defensive.
        return state

    s = RealmState.from_dict(state.to_dict())
    s.last_event_id = event.id

    et = event.type
    p = event.payload or {}

    if et == "realm.entered":
        # realm name is authoritative but kept consistent by service
        s.current_scene = p.get("scene") or s.current_scene
        return s

    if et == "time.tick":
        delta = int(p.get("delta") or 1)
        s.time += max(delta, 0)
        return s

    if et == "scene.set":
        s.current_scene = p.get("scene")
        return s

    if et == "flag.set":
        key = p.get("key")
        if isinstance(key, str) and key:
            s.flags[key] = p.get("value")
        return s

    if et == "entity.upsert":
        entity_id = p.get("entity_id")
        data = p.get("data") or {}
        if isinstance(entity_id, str) and entity_id and isinstance(data, dict):
            existing = deepcopy(s.entities.get(entity_id) or {})
            s.entities[entity_id] = _deep_merge(existing, data)
        return s

    if et == "location.upsert":
        location_id = p.get("location_id")
        data = p.get("data") or {}
        if isinstance(location_id, str) and location_id and isinstance(data, dict):
            existing = deepcopy(s.locations.get(location_id) or {})
            s.locations[location_id] = _deep_merge(existing, data)
        return s

    # Non-stateful events still advance last_event_id (already done).
    return s

