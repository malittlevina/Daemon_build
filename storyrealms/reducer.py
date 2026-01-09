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


def _ensure_rel(rel: Dict[str, Any], a: str, b: str) -> Dict[str, Any]:
    rel.setdefault(a, {})
    if not isinstance(rel[a], dict):
        rel[a] = {}
    rel[a].setdefault(b, {})
    if not isinstance(rel[a][b], dict):
        rel[a][b] = {}
    return rel[a][b]


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

    if et == "npc.goal.set":
        entity_id = p.get("entity_id")
        goal = p.get("goal")
        if isinstance(entity_id, str) and entity_id and isinstance(goal, str) and goal:
            s.goals.setdefault("npc", {})
            if not isinstance(s.goals["npc"], dict):
                s.goals["npc"] = {}
            # Store as list of goal strings per NPC.
            npc_goals = s.goals["npc"].get(entity_id)
            if not isinstance(npc_goals, list):
                npc_goals = []
            if goal not in npc_goals:
                npc_goals.append(goal)
            s.goals["npc"][entity_id] = npc_goals
        return s

    if et == "entity.upsert":
        entity_id = p.get("entity_id")
        data = p.get("data") or {}
        if isinstance(entity_id, str) and entity_id and isinstance(data, dict):
            existing = deepcopy(s.entities.get(entity_id) or {})
            s.entities[entity_id] = _deep_merge(existing, data)
        return s

    if et == "npc.plan.set":
        entity_id = p.get("entity_id")
        steps = p.get("steps")
        goal = p.get("goal")
        try:
            idx = int(p.get("idx") or 0)
        except Exception:
            idx = 0
        if isinstance(entity_id, str) and entity_id and isinstance(steps, list):
            existing = deepcopy(s.entities.get(entity_id) or {})
            if not isinstance(existing, dict):
                existing = {}
            existing["plan"] = {"goal": goal, "steps": list(steps), "idx": max(idx, 0)}
            s.entities[entity_id] = existing
        return s

    if et == "npc.plan.advance":
        entity_id = p.get("entity_id")
        try:
            delta = int(p.get("delta") or 1)
        except Exception:
            delta = 1
        if isinstance(entity_id, str) and entity_id:
            existing = deepcopy(s.entities.get(entity_id) or {})
            if isinstance(existing, dict) and isinstance(existing.get("plan"), dict):
                plan = deepcopy(existing["plan"])
                try:
                    idx = int(plan.get("idx") or 0)
                except Exception:
                    idx = 0
                plan["idx"] = max(idx + max(delta, 0), 0)
                existing["plan"] = plan
                s.entities[entity_id] = existing
        return s

    if et == "location.upsert":
        location_id = p.get("location_id")
        data = p.get("data") or {}
        if isinstance(location_id, str) and location_id and isinstance(data, dict):
            existing = deepcopy(s.locations.get(location_id) or {})
            s.locations[location_id] = _deep_merge(existing, data)
        return s

    if et == "relationship.adjust":
        a = p.get("a")
        b = p.get("b")
        delta = p.get("delta")
        if isinstance(a, str) and a and isinstance(b, str) and b and a != b:
            try:
                d = float(delta)
            except Exception:
                d = 0.0
            ab = _ensure_rel(s.relationships, a, b)
            ba = _ensure_rel(s.relationships, b, a)
            try:
                ab_trust = float(ab.get("trust") or 0.0) + d
            except Exception:
                ab_trust = d
            try:
                ba_trust = float(ba.get("trust") or 0.0) + d
            except Exception:
                ba_trust = d
            ab["trust"] = max(min(ab_trust, 1.0), -1.0)
            ba["trust"] = max(min(ba_trust, 1.0), -1.0)
        return s

    # Non-stateful events still advance last_event_id (already done).
    return s

