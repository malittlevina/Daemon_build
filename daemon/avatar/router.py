from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from daemon.avatar.events import AvatarEvent


def _emotion_to_expression(emotion: Optional[str]) -> Tuple[str, float]:
    """
    Map daemon emotion string to a VRM expression preset name + intensity.
    (Viewer implements these as best-effort; if missing, it just ignores.)
    """
    e = (emotion or "neutral").lower()
    if e in ("focused",):
        return ("serious", 0.8)
    if e in ("curious",):
        return ("relaxed", 0.6)
    if e in ("proud",):
        return ("happy", 0.7)
    if e in ("frustrated",):
        return ("angry", 0.6)
    return ("neutral", 0.0)


@dataclass
class AvatarRouter:
    """
    Convert Unimind signals/trace/plans into avatar events.

    This is intentionally rule-based and compact; deeper animation behaviors
    can later be learned/tuned using the same event channel.
    """

    def on_event_ingested(self, event: Dict[str, Any]) -> list[AvatarEvent]:
        et = str(event.get("type") or "")
        if et in {"text_input", "audio_transcript"}:
            return [AvatarEvent(type="state", payload={"name": "listening"})]
        if et == "vision_label":
            return [AvatarEvent(type="gesture", payload={"name": "nod", "intensity": 0.3})]
        return []

    def on_plan(self, *, plan: Any, trace: Any, ctx_signals: Dict[str, Any] | None = None) -> list[AvatarEvent]:
        out: list[AvatarEvent] = []

        # Emotion → expression
        emotion = None
        if ctx_signals and isinstance(ctx_signals, dict):
            emotion = (ctx_signals.get("emotion") or {}).get("current_emotion")
        expr, intensity = _emotion_to_expression(emotion)
        out.append(AvatarEvent(type="expression", payload={"name": expr, "intensity": intensity}))

        # Trace → state
        state_name = "thinking"
        try:
            selected = (getattr(trace, "selected", None) or {}) if trace else {}
            action = getattr(plan, "action", "") if plan else ""
            if isinstance(action, str) and action.startswith("trigger:"):
                state_name = "executing"
            elif isinstance(action, str) and action.startswith("[LAM]"):
                state_name = "thinking"
            else:
                state_name = "idle"
        except Exception:
            state_name = "thinking"
        out.append(AvatarEvent(type="state", payload={"name": state_name}))

        # Action → small gesture
        action = str(getattr(plan, "action", "") or "")
        if action.startswith("trigger:"):
            out.append(AvatarEvent(type="gesture", payload={"name": "wave", "intensity": 0.4}))
        elif action.startswith("explore:"):
            out.append(AvatarEvent(type="gesture", payload={"name": "nod", "intensity": 0.4}))

        # Speak event (optional text)
        utterance = None
        try:
            utterance = (getattr(trace, "notes", {}) or {}).get("utterance_plan", {}).get("text")
        except Exception:
            utterance = None
        if isinstance(utterance, str) and utterance.strip():
            out.append(AvatarEvent(type="speak", payload={"text": utterance.strip()}))

        # Debug: ship minimal info
        out.append(AvatarEvent(type="debug", payload={"action": action}))
        return out

