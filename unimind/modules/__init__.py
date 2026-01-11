# unimind/modules/__init__.py
"""
Cognitive Modules - Pluggable reasoning components for Unimind

Each module provides a specific cognitive capability that can be
registered with the Unimind core for integrated reasoning.
"""

from unimind.modules.logic_module import LogicModule
from unimind.modules.emotion_module import EmotionModule
from unimind.modules.memory_module import MemoryModule
from unimind.modules.intuition_module import IntuitionModule
from unimind.modules.ethics_module import EthicsModule

__all__ = [
    "LogicModule",
    "EmotionModule", 
    "MemoryModule",
    "IntuitionModule",
    "EthicsModule"
]
