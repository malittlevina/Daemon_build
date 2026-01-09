from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Protocol

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


class Rule(Protocol):
    """
    Deterministic rule that can emit derived events.
    """

    name: str

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]: ...


@dataclass(slots=True)
class NpcMoodFromWeatherRule:
    name: str = "npc.mood_from_weather"

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]:
        if event.type != "time.tick":
            return []

        derived: List[RealmEvent] = []
        weather = (state.flags or {}).get("weather")
        for npc_id in _npc_ids(state):
            npc = (state.entities or {}).get(npc_id) or {}
            if weather == "rain":
                mood = "pensive"
            elif weather == "sun":
                mood = "upbeat"
            else:
                mood = npc.get("mood") or "neutral"

            derived.append(
                RealmEvent(
                    type="entity.upsert",
                    realm=state.realm,
                    payload={"entity_id": npc_id, "data": {"mood": mood}},
                    meta={"derived_from": event.id, "rule": self.name},
                    actor="rule_engine",
                )
            )
            derived.append(
                RealmEvent(
                    type="npc.act",
                    realm=state.realm,
                    payload={"entity_id": npc_id, "act": "observe_weather", "mood": mood},
                    meta={"derived_from": event.id, "rule": self.name},
                    actor="rule_engine",
                )
            )
        return derived


@dataclass(slots=True)
class SceneAutoAdvanceRule:
    """
    Example narrative rule: advance scene every N ticks if enabled.

    Controlled by flags:
    - scene_auto: bool
    - scene_period: int (default 5)
    - scene_index: int (internal counter)
    """

    name: str = "scene.auto_advance"

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]:
        if event.type != "time.tick":
            return []
        flags = state.flags or {}
        if not flags.get("scene_auto"):
            return []
        try:
            period = int(flags.get("scene_period") or 5)
        except Exception:
            period = 5
        period = max(period, 1)

        idx = int(flags.get("scene_index") or 0) + 1
        derived: List[RealmEvent] = [
            RealmEvent(
                type="flag.set",
                realm=state.realm,
                payload={"key": "scene_index", "value": idx},
                meta={"derived_from": event.id, "rule": self.name},
                actor="rule_engine",
            )
        ]
        if idx % period == 0:
            next_scene = f"scene:{idx // period}"
            derived.append(
                RealmEvent(
                    type="scene.set",
                    realm=state.realm,
                    payload={"scene": next_scene},
                    meta={"derived_from": event.id, "rule": self.name},
                    actor="rule_engine",
                )
            )
            derived.append(
                RealmEvent(
                    type="narrative.beat",
                    realm=state.realm,
                    payload={"beat": "scene_advanced", "scene": next_scene},
                    meta={"derived_from": event.id, "rule": self.name},
                    actor="rule_engine",
                )
            )
        return derived


@dataclass(slots=True)
class NpcGoalPlannerRule:
    """
    Deterministic NPC layer 2: goals -> intents -> acts (on tick).

    Reads `state.goals["npc"][<npc_id>]` (list of goal strings).
    Emits:
    - npc.intent (non-stateful marker)
    - npc.act (non-stateful marker)
    - possibly entity.upsert / relationship.adjust via other rules
    """

    name: str = "npc.goal_planner"

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]:
        if event.type != "time.tick":
            return []

        npc_goals = (state.goals or {}).get("npc") or {}
        if not isinstance(npc_goals, dict):
            return []

        derived: List[RealmEvent] = []
        for npc_id in sorted(npc_goals.keys()):
            goals = npc_goals.get(npc_id)
            if not isinstance(goals, list) or not goals:
                continue
            # Deterministic choice: first goal string.
            goal = str(goals[0])

            # Deterministic intent mapping.
            if goal == "socialize":
                intent = "talk"
            elif goal == "explore":
                intent = "wander"
            else:
                intent = "idle"

            # Choose a deterministic target NPC (lowest other npc id).
            target_id = None
            if intent == "talk":
                others = [x for x in _npc_ids(state) if x != npc_id]
                target_id = others[0] if others else None

            derived.append(
                RealmEvent(
                    type="npc.intent",
                    realm=state.realm,
                    payload={"entity_id": npc_id, "goal": goal, "intent": intent, "target_id": target_id},
                    meta={"derived_from": event.id, "rule": self.name},
                    actor="rule_engine",
                )
            )
            derived.append(
                RealmEvent(
                    type="npc.act",
                    realm=state.realm,
                    payload={"entity_id": npc_id, "act": intent, "target_id": target_id},
                    meta={"derived_from": event.id, "rule": self.name},
                    actor="rule_engine",
                )
            )

        return derived


@dataclass(slots=True)
class SocialPhysicsRule:
    """
    Relationship + social physics:
    - 'talk' acts increase mutual trust slightly.
    """

    name: str = "social.physics"

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]:
        if event.type != "npc.act":
            return []
        p = event.payload or {}
        act = p.get("act")
        a = p.get("entity_id")
        b = p.get("target_id")
        if act != "talk":
            return []
        if not isinstance(a, str) or not isinstance(b, str) or not a or not b or a == b:
            return []
        return [
            RealmEvent(
                type="relationship.adjust",
                realm=state.realm,
                payload={"a": a, "b": b, "delta": 0.05},
                meta={"derived_from": event.id, "rule": self.name},
                actor="rule_engine",
            )
        ]


@dataclass(slots=True)
class RuleEngine:
    """
    Deterministic rule engine executed on tick.

    Produces additional events derived from current state + triggering event.
    """

    rules: List[Rule] = field(
        default_factory=lambda: [
            NpcMoodFromWeatherRule(),
            SceneAutoAdvanceRule(),
            NpcGoalPlannerRule(),
            SocialPhysicsRule(),
        ]
    )

    def on_event(self, state: RealmState, event: RealmEvent) -> List[RealmEvent]:
        derived: List[RealmEvent] = []
        for rule in list(self.rules):
            try:
                derived.extend(rule.on_event(state, event))
            except Exception as e:
                print(f"[Storyrealms][Rules] rule '{getattr(rule, 'name', 'unknown')}' error: {e}")
        return derived

