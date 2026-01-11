from __future__ import annotations

from typing import Any

from unimind.context import UnimindContext


class EmotionModule:
    """
    Updates emotional state based on stimulus.
    """

    def __init__(self, emotion_engine):
        self.emotions = emotion_engine

    def process(self, user_input: str, context: UnimindContext) -> None:
        stimulus = str(context.get("output") or user_input or "").strip().lower()
        try:
            self.emotions.update_emotion(stimulus)
            context.set("emotion", self.emotions.get_emotion())
        except Exception:
            context.set("emotion", "unknown")
        context.emit("emotion_updated", context.get("emotion"))
        return None

