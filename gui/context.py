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

