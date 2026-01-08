from __future__ import annotations

from typing import Any, Dict

from daemon.state_manager import StateManager
from kernel.services import Service
from rituals.ritual_registry import RitualRegistry
from unimind.core import Unimind


class StateService:
    name = "state"

    def __init__(self, state: StateManager):
        self._state = state

    def state(self) -> Dict[str, Any]:
        return dict(self._state.state)

    def health(self) -> Dict[str, Any]:
        return {"ok": True}


class RitualsService:
    name = "rituals"

    def __init__(self, rituals: RitualRegistry):
        self._rituals = rituals

    def state(self) -> Dict[str, Any]:
        return {
            "registered": list(getattr(self._rituals, "registered_rituals", {}).keys()),
            "dynamic": list(getattr(self._rituals, "dynamic_rituals", {}).keys()),
        }

    def health(self) -> Dict[str, Any]:
        return {"ok": True}


class UnimindService:
    name = "unimind"

    def __init__(self, unimind: Unimind):
        self._unimind = unimind

    def state(self) -> Dict[str, Any]:
        modules = getattr(self._unimind, "modules", {})
        return {"modules": {k: len(v) for k, v in modules.items()} if isinstance(modules, dict) else {}}

    def health(self) -> Dict[str, Any]:
        return {"ok": True}

