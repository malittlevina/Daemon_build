from __future__ import annotations

from typing import Any, Dict, List, Optional

from storyrealms.events import RealmEvent
from storyrealms.state import RealmState


def _npc_ids(state: RealmState) -> List[str]:
    ids: List[str] = []
    for eid, data in (state.entities or {}).items():
        if isinstance(data, dict) and (data.get("kind") == "npc" or str(eid).startswith("npc:")):
            ids.append(str(eid))
    return sorted(ids)


def build_realm_view(state: RealmState, events: Optional[List[RealmEvent]] = None) -> Dict[str, Any]:
    """
    UX/HUD-ready JSON view model for a realm.

    This should be stable for UIs, while internal state can evolve independently.
    """
    npc_ids = _npc_ids(state)
    npc_cards = []
    for nid in npc_ids[:20]:
        d = (state.entities or {}).get(nid) or {}
        if isinstance(d, dict):
            npc_cards.append(
                {
                    "id": nid,
                    "name": d.get("name"),
                    "mood": d.get("mood"),
                    "loc": d.get("location"),
                }
            )
        else:
            npc_cards.append({"id": nid, "value": d})

    timeline = []
    for ev in (events or [])[-50:]:
        timeline.append(
            {
                "ts": ev.ts,
                "type": ev.type,
                "id": ev.id,
                "actor": ev.actor,
                "summary": ev.type,
                "payload": ev.payload,
            }
        )

    return {
        "schema": {"state_version": state.schema_version},
        "realm": state.realm,
        "time": {"tick": state.time},
        "scene": {"current": state.current_scene},
        "counts": {
            "entities": len(state.entities or {}),
            "locations": len(state.locations or {}),
            "npcs": len(npc_ids),
        },
        "flags": dict(state.flags or {}),
        "goals": dict(state.goals or {}),
        "npcs": npc_cards,
        "timeline": timeline,
    }

