# storyrealms/storyrealm_bridge.py

"""
Compatibility bridge for Storyrealms (world engine).

This file preserves the original simple functions while delegating to the
event-sourced StoryrealmsService underneath.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from storyrealms.service import StoryrealmsService


_SERVICE: Optional[StoryrealmsService] = None


def _service() -> StoryrealmsService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = StoryrealmsService()
    return _SERVICE


def enter_storyrealm(realm_name: str):
    return _service().enter_realm(realm_name, actor="storyrealm_bridge")


def push_event_to_realm(event_data: dict):
    # Back-compat: treat incoming dict as a generic realm event.
    event_type = str(event_data.get("type") or "realm.event")
    payload: Dict[str, Any] = dict(event_data.get("payload") or {})
    meta: Dict[str, Any] = dict(event_data.get("meta") or {})
    actor = event_data.get("actor")
    realm = event_data.get("realm")
    return _service().emit_event(event_type, payload, realm=realm, actor=actor, meta=meta)


def get_current_realm():
    return {"current_realm": _service().current_realm}


def list_realm_events():
    # Compatibility: return recent events + current state snapshot.
    svc = _service()
    return {
        "events": svc.list_events(limit=200).get("events", []),
        "state": svc.query_state(),
    }
