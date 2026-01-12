# emotion/__init__.py
"""
Emotion Engine
==============
Emotional state management for the daemon.
"""

from .emotion_engine import EmotionEngine, emotion_state, update_emotional_state

__all__ = [
    'EmotionEngine',
    'emotion_state',
    'update_emotional_state',
]
