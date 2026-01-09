# world_engine/time/time_manager.py
"""
Time Manager - World time control and management.

Provides:
- World time tracking (separate from real time)
- Time scaling (slow motion, fast forward)
- Pause/resume
- Time-based scheduling
- Day/night cycles
"""

from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import time as real_time
import uuid


class TimeScale(Enum):
    """Predefined time scales."""
    FROZEN = 0.0
    SLOW_MOTION = 0.25
    HALF_SPEED = 0.5
    NORMAL = 1.0
    FAST = 2.0
    VERY_FAST = 5.0
    INSTANT = 100.0


@dataclass
class ScheduledEvent:
    """An event scheduled to occur at a specific world time."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "event"
    trigger_time: float = 0.0
    callback: Callable = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    recurring: bool = False
    interval: float = 0.0
    executed: bool = False
    cancelled: bool = False


class TimeManager:
    """
    Manages world time for the simulation.
    
    Features:
    - World time tracking (independent of real time)
    - Time scaling (slow motion, pause, fast forward)
    - Day/night cycle support
    - Scheduled events
    """
    
    def __init__(self, world):
        """Initialize the time manager."""
        self.world = world
        
        # Current world time (in seconds)
        self._current_time: float = 0.0
        
        # Time scale (1.0 = real time)
        self._time_scale: float = 1.0
        
        # Paused state
        self._paused: bool = False
        
        # Real time tracking
        self._real_start_time: float = real_time.time()
        self._last_update_time: float = self._real_start_time
        
        # Day/night cycle
        self._day_length: float = 86400.0  # Seconds in a day
        self._time_of_day: float = 43200.0  # Start at noon
        
        # Scheduled events
        self._events: Dict[str, ScheduledEvent] = {}
        
        # Time listeners
        self._on_tick: List[Callable[[float, float], None]] = []
        self._on_hour: List[Callable[[int], None]] = []
        self._on_day: List[Callable[[int], None]] = []
        
        # Statistics
        self._total_paused_time: float = 0.0
        self._day_count: int = 0
        self._last_hour: int = -1
        
        print("[TimeManager] Initialized")
    
    # =========================================================================
    # Time access
    # =========================================================================
    
    @property
    def current_time(self) -> float:
        """Get current world time in seconds."""
        return self._current_time
    
    @property
    def time_scale(self) -> float:
        """Get current time scale."""
        return self._time_scale
    
    @property
    def is_paused(self) -> bool:
        """Check if time is paused."""
        return self._paused
    
    @property
    def time_of_day(self) -> float:
        """Get time of day in seconds (0 to day_length)."""
        return self._time_of_day
    
    @property
    def day_progress(self) -> float:
        """Get day progress as 0-1."""
        return self._time_of_day / self._day_length
    
    @property
    def hour(self) -> int:
        """Get current hour (0-23)."""
        return int((self._time_of_day / self._day_length) * 24) % 24
    
    @property
    def minute(self) -> int:
        """Get current minute (0-59)."""
        hour_progress = (self._time_of_day % (self._day_length / 24))
        return int((hour_progress / (self._day_length / 24)) * 60)
    
    @property
    def is_day(self) -> bool:
        """Check if it's daytime (6 AM - 6 PM)."""
        hour = self.hour
        return 6 <= hour < 18
    
    @property
    def is_night(self) -> bool:
        """Check if it's nighttime."""
        return not self.is_day
    
    # =========================================================================
    # Time control
    # =========================================================================
    
    def advance(self, dt: float):
        """
        Advance world time by dt seconds.
        
        This is called by the world engine each tick.
        """
        if self._paused:
            return
        
        # Apply time scale
        scaled_dt = dt * self._time_scale
        
        # Update world time
        self._current_time += scaled_dt
        
        # Update time of day
        old_hour = self.hour
        self._time_of_day += scaled_dt
        
        # Handle day rollover
        while self._time_of_day >= self._day_length:
            self._time_of_day -= self._day_length
            self._day_count += 1
            
            # Fire day callbacks
            for callback in self._on_day:
                callback(self._day_count)
        
        # Check hour change
        new_hour = self.hour
        if new_hour != old_hour:
            self._last_hour = new_hour
            for callback in self._on_hour:
                callback(new_hour)
        
        # Process scheduled events
        self._process_events()
        
        # Fire tick callbacks
        for callback in self._on_tick:
            callback(self._current_time, scaled_dt)
    
    def set_time_scale(self, scale: float):
        """Set time scale."""
        self._time_scale = max(0.0, scale)
    
    def set_time_scale_preset(self, preset: TimeScale):
        """Set time scale from preset."""
        self._time_scale = preset.value
    
    def pause(self):
        """Pause time."""
        if not self._paused:
            self._paused = True
            self._pause_start = real_time.time()
    
    def resume(self):
        """Resume time."""
        if self._paused:
            self._paused = False
            self._total_paused_time += real_time.time() - self._pause_start
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self._paused:
            self.resume()
        else:
            self.pause()
    
    def set_time(self, world_time: float):
        """Set the current world time."""
        self._current_time = world_time
    
    def set_time_of_day(self, seconds: float):
        """Set the time of day in seconds."""
        self._time_of_day = seconds % self._day_length
    
    def set_hour(self, hour: int):
        """Set the hour of day (0-23)."""
        self._time_of_day = (hour / 24.0) * self._day_length
    
    def set_day_length(self, seconds: float):
        """Set the length of a day in seconds."""
        old_progress = self.day_progress
        self._day_length = seconds
        self._time_of_day = old_progress * seconds
    
    # =========================================================================
    # Scheduled events
    # =========================================================================
    
    def schedule(
        self,
        callback: Callable,
        delay: float,
        name: str = "event",
        args: tuple = (),
        kwargs: Dict[str, Any] = None
    ) -> str:
        """Schedule an event to occur after a delay."""
        event = ScheduledEvent(
            name=name,
            trigger_time=self._current_time + delay,
            callback=callback,
            args=args,
            kwargs=kwargs or {}
        )
        self._events[event.id] = event
        return event.id
    
    def schedule_at(
        self,
        callback: Callable,
        world_time: float,
        name: str = "event",
        args: tuple = (),
        kwargs: Dict[str, Any] = None
    ) -> str:
        """Schedule an event at a specific world time."""
        event = ScheduledEvent(
            name=name,
            trigger_time=world_time,
            callback=callback,
            args=args,
            kwargs=kwargs or {}
        )
        self._events[event.id] = event
        return event.id
    
    def schedule_recurring(
        self,
        callback: Callable,
        interval: float,
        name: str = "recurring",
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        start_delay: float = 0
    ) -> str:
        """Schedule a recurring event."""
        event = ScheduledEvent(
            name=name,
            trigger_time=self._current_time + start_delay + interval,
            callback=callback,
            args=args,
            kwargs=kwargs or {},
            recurring=True,
            interval=interval
        )
        self._events[event.id] = event
        return event.id
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event."""
        if event_id in self._events:
            self._events[event_id].cancelled = True
            del self._events[event_id]
            return True
        return False
    
    def _process_events(self):
        """Process due events."""
        to_remove = []
        to_reschedule = []
        
        for event_id, event in self._events.items():
            if event.cancelled:
                to_remove.append(event_id)
                continue
            
            if self._current_time >= event.trigger_time:
                # Execute event
                try:
                    event.callback(*event.args, **event.kwargs)
                except Exception as e:
                    print(f"[TimeManager] Event error: {e}")
                
                event.executed = True
                
                if event.recurring:
                    # Reschedule
                    event.trigger_time = self._current_time + event.interval
                    event.executed = False
                else:
                    to_remove.append(event_id)
        
        for event_id in to_remove:
            del self._events[event_id]
    
    # =========================================================================
    # Listeners
    # =========================================================================
    
    def on_tick(self, callback: Callable[[float, float], None]):
        """Register a tick callback (time, dt)."""
        self._on_tick.append(callback)
    
    def on_hour_change(self, callback: Callable[[int], None]):
        """Register an hour change callback."""
        self._on_hour.append(callback)
    
    def on_day_change(self, callback: Callable[[int], None]):
        """Register a day change callback."""
        self._on_day.append(callback)
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def get_real_elapsed(self) -> float:
        """Get real elapsed time since start."""
        return real_time.time() - self._real_start_time - self._total_paused_time
    
    def format_time(self) -> str:
        """Format current time as HH:MM."""
        return f"{self.hour:02d}:{self.minute:02d}"
    
    def format_time_full(self) -> str:
        """Format current time with day."""
        return f"Day {self._day_count + 1}, {self.format_time()}"
    
    def get_sun_angle(self) -> float:
        """Get sun angle (0 = midnight, 180 = noon)."""
        return self.day_progress * 360.0
    
    def get_light_level(self) -> float:
        """Get ambient light level (0-1)."""
        import math
        # Simple sinusoidal day/night cycle
        angle_rad = math.radians(self.get_sun_angle() - 90)
        return max(0, math.sin(angle_rad))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get time statistics."""
        return {
            "world_time": self._current_time,
            "time_scale": self._time_scale,
            "paused": self._paused,
            "time_of_day": self.format_time(),
            "day_count": self._day_count,
            "is_day": self.is_day,
            "light_level": self.get_light_level(),
            "pending_events": len(self._events),
            "real_elapsed": self.get_real_elapsed()
        }
