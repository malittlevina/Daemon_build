from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class RobotCapabilities:
    """
    Declare what a driver/hardware can do.
    Keep this intentionally small and extensible.
    """

    mobility: bool = True
    follow_mode: bool = True
    stop: bool = True
    lights: bool = False
    manipulator: bool = False


@dataclass(frozen=True)
class RobotCommand:
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    timestamp_utc: Optional[str] = None


@dataclass
class RobotTelemetry:
    status: str = "idle"
    battery_pct: float = 100.0
    x_m: float = 0.0
    y_m: float = 0.0
    heading_deg: float = 0.0
    mode: str = "idle"  # e.g. idle | follow | manual
    extra: Dict[str, Any] = field(default_factory=dict)

