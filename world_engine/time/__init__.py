# world_engine/time/__init__.py
"""
Time management for the World Engine.

Provides:
- World time tracking
- Time scaling
- Pause/resume
- Time-based events
"""

from world_engine.time.time_manager import TimeManager, TimeScale

__all__ = [
    "TimeManager",
    "TimeScale"
]
