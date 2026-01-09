from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from storyrealms.events import RealmEvent
from storyrealms.state import RealmState


def _npc_ids(state: RealmState) -> List[str]:
    ids = []
    for eid, data in (state.entities or {}).items():
        if not isinstance(data, dict):
            continue
        if data.get("kind") == "npc" or str(eid).startswith("npc:"):
            ids.append(eid)
    return ids


@dataclass(slots=True)
class RuleEngine:
    """
    Deterministic rule engine executed on tick.

    Produces additional events derived from current state + triggering event.
    """

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]:
        if event.type != "time.tick":
            return []

        derived: List[RealmEvent] = []
        weather = (state.flags or {}).get("weather")
        for npc_id in _npc_ids(state):
            npc = (state.entities or {}).get(npc_id) or {}
            # Simple deterministic policy: weather influences mood.
            if weather == "rain":
                mood = "pensive"
            elif weather == "sun":
                mood = "upbeat"
            else:
                mood = npc.get("mood") or "neutral"

            # Emit a stateful upsert and a narrative act marker.
            derived.append(
                RealmEvent(
                    type="entity.upsert",
                    realm=state.realm,
                    payload={"entity_id": npc_id, "data": {"mood": mood}},
                    meta={"derived_from": event.id, "rule": "npc.mood_from_weather"},
                    actor="rule_engine",
                )
            )
            derived.append(
                RealmEvent(
                    type="npc.act",
                    realm=state.realm,
                    payload={"entity_id": npc_id, "act": "observe_weather", "mood": mood},
                    meta={"derived_from": event.id},
                    actor="rule_engine",
                )
            )

        return derived

