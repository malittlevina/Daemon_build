from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from unimind.context import UnimindContext


@runtime_checkable
class UnimindSubsystem(Protocol):
    """
    Agent-native subsystem interface.

    Subsystems are optional-capability: implement what makes sense and Unimind
    will call it opportunistically.
    """

    name: str

    def observe(self, ctx: UnimindContext) -> Dict[str, Any]:
        ...

    def think(self, ctx: UnimindContext) -> Optional[Dict[str, Any]]:
        ...


@dataclass(frozen=True)
class SubsystemReport:
    name: str
    observation: Dict[str, Any]
    thought: Optional[Dict[str, Any]] = None


class EmotionSubsystem:
    name = "emotion"

    def __init__(self, engine: Any):
        self._engine = engine

    def observe(self, ctx: UnimindContext) -> Dict[str, Any]:
        get_emotion = getattr(self._engine, "get_emotion", None)
        current = get_emotion() if callable(get_emotion) else None
        return {"current_emotion": current}

    def think(self, ctx: UnimindContext) -> Optional[Dict[str, Any]]:
        update_emotion = getattr(self._engine, "update_emotion", None)
        if callable(update_emotion) and ctx.intent:
            try:
                update_emotion(str(ctx.intent))
            except Exception:
                # Keep Unimind robust: emotion is a soft signal.
                pass
        return None


class MemorySubsystem:
    name = "memory"

    def __init__(self, logger: Any):
        self._logger = logger

    def observe(self, ctx: UnimindContext) -> Dict[str, Any]:
        get_latest = getattr(self._logger, "get_latest_events", None)
        events = get_latest(5) if callable(get_latest) else []
        return {"recent_events": events}

    def think(self, ctx: UnimindContext) -> Optional[Dict[str, Any]]:
        log_event = getattr(self._logger, "log_event", None)
        if callable(log_event) and ctx.input_text:
            try:
                log_event(
                    "user_input",
                    ctx.input_text,
                    context={
                        "intent": ctx.intent,
                        "symbolic_state": ctx.symbolic_state,
                    },
                )
            except Exception:
                pass
        return None


class EthicsSubsystem:
    name = "ethics"

    def __init__(self, ethical_core: Any):
        self._core = ethical_core

    def observe(self, ctx: UnimindContext) -> Dict[str, Any]:
        list_principles = getattr(self._core, "list_principles", None)
        principles = list_principles() if callable(list_principles) else []
        return {"principles": principles}

    def think(self, ctx: UnimindContext) -> Optional[Dict[str, Any]]:
        # Ethics is used during plan selection; no autonomous thinking here.
        return None

    def evaluate(self, action: str) -> Optional[str]:
        evaluate_action = getattr(self._core, "evaluate_action", None)
        if callable(evaluate_action):
            try:
                return str(evaluate_action(action))
            except Exception:
                return None
        return None


class LamSubsystem:
    name = "logic"

    def __init__(self, lam_state_module: Any, lam_planner_module: Any):
        self._state = lam_state_module
        self._planner = lam_planner_module

    def observe(self, ctx: UnimindContext) -> Dict[str, Any]:
        state = getattr(self._state, "symbolic_state", None)
        return {"symbolic_state": state if isinstance(state, dict) else {}}

    def think(self, ctx: UnimindContext) -> Optional[Dict[str, Any]]:
        plan_next = getattr(self._planner, "plan_next_action", None)
        if callable(plan_next) and ctx.input_text:
            try:
                symbolic_state = getattr(self._state, "symbolic_state", {}) or {}
                plan = plan_next(ctx.input_text, symbolic_state)
                return {"lam_plan": plan}
            except Exception as e:
                return {"lam_plan_error": str(e)}
        return None
