from __future__ import annotations

from typing import Any, Dict, Optional


class EmotionModule:
    """
    Updates emotional state based on stimulus.
    """

    def __init__(self, emotion_engine):
        self.emotions = emotion_engine

    def process(self, user_input: str, context: Dict[str, Any]) -> None:
        stimulus = str(context.get("output") or user_input or "").strip().lower()
        try:
            self.emotions.update_emotion(stimulus)
            context["emotion"] = self.emotions.get_emotion()
        except Exception:
            context["emotion"] = "unknown"
        return None

