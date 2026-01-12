# unimind/__init__.py
"""
Unimind - The Daemon's Central Cortex
=====================================
The unified mind that coordinates all cognitive functions.

Unimind acts as:
- Event Bus: Routes signals between brain regions
- Thought Pipeline: Coordinates LLM/NLU/LAM processing
- Working Memory: Maintains current context
- Attention System: Prioritizes processing
"""

from .core import (
    Unimind,
    Signal,
    SignalType,
    BrainRegion,
    WorkingMemory,
    get_unimind,
    think
)
from .decision_matrix import DecisionMatrix
from .cognition import CognitionPipeline, ThoughtResult

__all__ = [
    'Unimind',
    'Signal',
    'SignalType',
    'BrainRegion',
    'WorkingMemory',
    'get_unimind',
    'think',
    'DecisionMatrix',
    'CognitionPipeline',
    'ThoughtResult',
]
