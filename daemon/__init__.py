# daemon/__init__.py
"""
Daemon - The AI Companion Core
==============================
The daemon is a standalone AI companion that operates independently.
It can optionally connect to ThothOS but does not require it.

The daemon provides:
- Natural language understanding and generation
- Memory and learning
- Device interaction and observation
- Task planning and execution
- Emotional awareness
- Personal assistance
"""

from .state_manager import StateManager
from .daemon_core import Daemon, DaemonConfig

__all__ = [
    'StateManager',
    'Daemon',
    'DaemonConfig',
]
