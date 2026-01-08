from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.event_bus import EventBus, GLOBAL_EVENT_BUS
from daemon.state_manager import StateManager
from rituals.ritual_registry import RitualRegistry
from unimind.core import Unimind


@dataclass
class DaemonUIContext:
    """
    Context adapter: exposes daemon+Unimind as an AI-friendly UI contract.
    Keeps coupling shallow by providing:
    - state snapshot
    - action catalog
    - action invocation entrypoint
    """

    unimind: Unimind
    rituals: RitualRegistry
    state: StateManager
    event_bus: EventBus = GLOBAL_EVENT_BUS

    def get_state(self) -> Dict[str, Any]:
        registered = list(getattr(self.rituals, "registered_rituals", {}).keys())
        dynamic = list(getattr(self.rituals, "dynamic_rituals", {}).keys())
        modules = getattr(self.unimind, "modules", {})

        return {
            "daemon": {
                "paused": bool(self.state.get("is_paused")),
                "scroll_count": int(self.state.get("scroll_count") or 0),
                "last_run": self.state.get("last_run"),
            },
            "unimind": {
                "modules": {k: len(v) for k, v in modules.items()} if isinstance(modules, dict) else {},
            },
            "rituals": {
                "registered": registered,
                "dynamic": dynamic,
            },
            "events_recent": self.event_bus.recent(limit=50),
        }

    def list_actions(self) -> List[Dict[str, Any]]:
        # A minimal “action surface” to start; can expand into schemas later.
        return [
            {
                "name": "daemon.toggle_pause",
                "description": "Toggle daemon paused state",
                "args_schema": {},
            },
            {
                "name": "unimind.reflect",
                "description": "Run Unimind reflection loop",
                "args_schema": {},
            },
            {
                "name": "ritual.cast",
                "description": "Cast a ritual by name",
                "args_schema": {"ritual_name": "string", "context": "object (optional)"},
            },
        ]

    def get_world_model(self) -> Dict[str, Any]:
        """
        Minimal world model graph (nodes + edges).

        This is intentionally simple and stable; we can enrich it with:
        - sensor confidence
        - health/latency metrics
        - memory pointers/citations
        - active goals/plans
        """

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        def add_node(node_id: str, label: str, kind: str, meta: Optional[Dict[str, Any]] = None) -> None:
            nodes.append({"id": node_id, "label": label, "kind": kind, "meta": meta or {}})

        def add_edge(src: str, dst: str, rel: str) -> None:
            edges.append({"from": src, "to": dst, "rel": rel})

        add_node("daemon:prometheus", "Prometheus (daemon)", "daemon")
        add_node("unimind:core", "Unimind", "agent", meta={"module_counts": self.get_state().get("unimind", {}).get("modules", {})})
        add_node("rituals:registry", "RitualRegistry", "registry", meta={"registered": len(getattr(self.rituals, "registered_rituals", {})), "dynamic": len(getattr(self.rituals, "dynamic_rituals", {}))})
        add_node("state:manager", "StateManager", "state")
        add_node("events:bus", "EventBus", "events")

        add_edge("daemon:prometheus", "unimind:core", "hosts")
        add_edge("daemon:prometheus", "rituals:registry", "routes_commands_to")
        add_edge("daemon:prometheus", "state:manager", "persists_state_in")
        add_edge("daemon:prometheus", "events:bus", "publishes_events_to")
        add_edge("unimind:core", "events:bus", "publishes_events_to")
        add_edge("rituals:registry", "events:bus", "publishes_events_to")
        add_edge("state:manager", "events:bus", "publishes_events_to")

        # Ritual nodes (top-level only, to keep graph readable)
        for r in list(getattr(self.rituals, "registered_rituals", {}).keys()):
            rid = f"ritual:{r}"
            add_node(rid, r, "ritual", meta={"type": "registered"})
            add_edge("rituals:registry", rid, "registers")
        for r in list(getattr(self.rituals, "dynamic_rituals", {}).keys()):
            rid = f"ritual:{r}"
            add_node(rid, r, "ritual", meta={"type": "dynamic"})
            add_edge("rituals:registry", rid, "registers")

        return {"version": "0.1", "nodes": nodes, "edges": edges}

    def invoke_action(self, name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args = args or {}

        if name == "daemon.toggle_pause":
            new_state = self.state.toggle_pause()
            self.event_bus.publish(
                "daemon.pause_toggled",
                {"paused": bool(new_state)},
                source="ui",
                tags=["daemon", "state"],
            )
            return {"paused": bool(new_state)}

        if name == "unimind.reflect":
            self.event_bus.publish("unimind.reflect.start", {}, source="ui", tags=["unimind"])
            self.unimind.reflect()
            self.event_bus.publish("unimind.reflect.end", {}, source="ui", tags=["unimind"])
            return {"ok": True}

        if name == "ritual.cast":
            ritual_name = str(args.get("ritual_name", "")).strip()
            context = args.get("context") or {}
            self.event_bus.publish(
                "ritual.cast.request",
                {"ritual_name": ritual_name, "context": context},
                source="ui",
                tags=["rituals"],
            )
            result = self.rituals.cast_ritual(ritual_name, context=context)
            self.event_bus.publish(
                "ritual.cast.result",
                {"ritual_name": ritual_name, "result": result},
                source="ui",
                tags=["rituals"],
            )
            return {"result": result}

        raise ValueError(f"Unknown action: {name}")

