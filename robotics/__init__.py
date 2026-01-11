"""
Robotics subsystem (safe-by-default).

This package provides:
- A driver interface (simulation now, hardware later)
- A safety/policy gate (arming, speed limits, ethics checks)
- A text-command handler so the daemon can control a robot via intents
"""

from robotics.robotics_manager import get_robotics_manager  # noqa: F401

