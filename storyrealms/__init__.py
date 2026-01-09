"""
Storyrealms: the "world engine" subsystem.

This package provides an agent-native realm runtime:
- event-sourced state transitions (deterministic replay)
- persistence (event log + snapshots)
- integrations (memory logging, scroll triggers) via soft imports
"""

from storyrealms.service import StoryrealmsService

__all__ = ["StoryrealmsService"]

