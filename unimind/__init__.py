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

Enhanced Cognition provides:
- Task Classification: Determines what output is needed
- Capability Routing: Routes to appropriate subsystems
- Multimodal Generation: Image, video, audio, 3D, code
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

# Enhanced cognition with multimodal support
from .enhanced_cognition import (
    EnhancedCognitionPipeline,
    EnhancedNLUProcessor,
    TaskClassifier,
    CapabilityRouter,
    GenerationInterface,
    OutputType,
    Capability,
    TaskClassification,
    EnhancedThoughtResult,
    get_enhanced_cognition,
    create_enhanced_cognition,
)

__all__ = [
    # Core
    'Unimind',
    'Signal',
    'SignalType',
    'BrainRegion',
    'WorkingMemory',
    'get_unimind',
    'think',
    'DecisionMatrix',
    
    # Base cognition
    'CognitionPipeline',
    'ThoughtResult',
    
    # Enhanced cognition
    'EnhancedCognitionPipeline',
    'EnhancedNLUProcessor',
    'TaskClassifier',
    'CapabilityRouter',
    'GenerationInterface',
    'OutputType',
    'Capability',
    'TaskClassification',
    'EnhancedThoughtResult',
    'get_enhanced_cognition',
    'create_enhanced_cognition',
]
