from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from storyrealms.bus import EventBus
from storyrealms.events import RealmEvent
from storyrealms.integrations import compose_sinks, memory_logger_sink, scroll_trigger_sink
from storyrealms.persistence import StoryrealmsStore
from storyrealms.reducer import apply_event
from storyrealms.rules import RuleEngine
from storyrealms.state import RealmState


@dataclass(slots=True)
class StoryrealmsService:
    """
    Primary API for the world engine / Storyrealms subsystem.

    This is the boundary other subsystems should call into:
    - bridges (XR/UI/network)
    - NLU intent handlers
    - Scroll actions that mutate world state
    - planners querying state
    """

    store: StoryrealmsStore = field(default_factory=StoryrealmsStore)
    bus: EventBus = field(default_factory=EventBus)
    rules: RuleEngine = field(default_factory=RuleEngine)
    snapshot_every: int = 1
    current_realm: str = "default"
    _states: Dict[str, RealmState] = field(default_factory=dict)
    _event_counts: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Default integrations are soft/optional.
        self.bus.subscribe(compose_sinks(memory_logger_sink, scroll_trigger_sink))

    def _get_or_load_state(self, realm: str) -> RealmState:
        realm = realm.strip() or "default"
        if realm in self._states:
            return self._states[realm]

        snap = self.store.load_snapshot(realm)
        if snap is None:
            snap = RealmState(realm=realm)

        # Apply any events after snapshot's last_event_id (linear scan).
        state = snap
        seen_snapshot_event = snap.last_event_id is None
        for ev in self.store.iter_events(realm):
            if not seen_snapshot_event:
                if ev.id == snap.last_event_id:
                    seen_snapshot_event = True
                continue
            state = apply_event(state, ev)

        self._states[realm] = state
        return state

    def enter_realm(self, realm_name: str, actor: Optional[str] = None, scene: Optional[str] = None) -> Dict[str, Any]:
        realm_name = realm_name.strip() or "default"
        self.current_realm = realm_name
        _ = self._get_or_load_state(realm_name)
        ev = RealmEvent(
            type="realm.entered",
            realm=realm_name,
            actor=actor,
            payload={"scene": scene} if scene else {},
        )
        self._record(ev)
        return {"status": "entered", "realm": realm_name}

    def emit_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        realm: Optional[str] = None,
        actor: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        r = (realm or self.current_realm).strip() or "default"
        _ = self._get_or_load_state(r)
        ev = RealmEvent(type=event_type, realm=r, actor=actor, payload=payload or {}, meta=meta or {})
        self._record(ev)
        return {"status": "event_emitted", "event": ev.to_dict()}

    def dispatch_command(
        self,
        command: str,
        args: Optional[Dict[str, Any]] = None,
        *,
        realm: Optional[str] = None,
        actor: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {"command": command, "args": args or {}}
        return self.emit_event(
            "command.dispatched",
            payload,
            realm=realm,
            actor=actor,
            meta=meta,
        )

    def tick(self, delta: int = 1, *, realm: Optional[str] = None, actor: Optional[str] = None) -> Dict[str, Any]:
        return self.emit_event("time.tick", {"delta": int(delta)}, realm=realm, actor=actor)

    def query_state(self, *, realm: Optional[str] = None) -> Dict[str, Any]:
        r = (realm or self.current_realm).strip() or "default"
        state = self._get_or_load_state(r)
        return {"realm": r, "state": state.to_dict()}

    def replay(self, *, realm: Optional[str] = None) -> Dict[str, Any]:
        r = (realm or self.current_realm).strip() or "default"
        snap = self.store.load_snapshot(r)
        if snap is None:
            state = RealmState(realm=r)
            for ev in self.store.iter_events(r):
                state = apply_event(state, ev)
        else:
            state = snap
            seen_snapshot_event = snap.last_event_id is None
            for ev in self.store.iter_events(r):
                if not seen_snapshot_event:
                    if ev.id == snap.last_event_id:
                        seen_snapshot_event = True
                    continue
                state = apply_event(state, ev)
        self._states[r] = state
        return {"realm": r, "state": state.to_dict(), "status": "replayed"}

    def list_events(self, *, realm: Optional[str] = None, limit: Optional[int] = 100) -> Dict[str, Any]:
        r = (realm or self.current_realm).strip() or "default"
        events = self.store.read_events(r, limit=limit)
        return {"realm": r, "events": [e.to_dict() for e in events]}

    def _record(self, event: RealmEvent) -> None:
        # Apply deterministically, then persist.
        state = self._get_or_load_state(event.realm)
        new_state = apply_event(state, event)
        self._states[event.realm] = new_state

        self.store.append_event(event)
        # Snapshot cadence (default: every event).
        n = int(self._event_counts.get(event.realm, 0)) + 1
        self._event_counts[event.realm] = n
        every = max(int(self.snapshot_every or 1), 1)
        if n % every == 0:
            self.store.save_snapshot(new_state)

        self.bus.publish(event)

        # Derived events (rules) after primary event is recorded.
        try:
            derived = self.rules.on_event(new_state, event)
        except Exception as e:
            print(f"[Storyrealms][Rules] error: {e}")
            derived = []
        for dev in derived:
            # Record derived events as first-class events (they are part of replay).
            self._record(dev)

