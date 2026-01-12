# nlu/__init__.py
"""
NLU - Natural Language Understanding
=====================================
Provides natural language understanding capabilities for the daemon.
"""

from .nlu_engine import NLUEngine
from .device_commands import DeviceCommandHandler, handle_device_command

__all__ = [
    'NLUEngine',
    'DeviceCommandHandler',
    'handle_device_command',
]
