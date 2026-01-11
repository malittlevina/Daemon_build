# unimind/__init__.py
# Unimind - Advanced Cognitive Architecture for ThothOS Daemon

from unimind.core import Unimind
from unimind.decision_matrix import DecisionMatrix
from unimind.neural_bus import NeuralBus, NeuralSignal, SignalType, Priority, get_neural_bus
from unimind.cortex import (
    UnimindCortex, 
    WorkingMemory, 
    CognitiveState, 
    ConsciousnessLevel,
    ThoughtUnit,
    Goal,
    get_cortex
)

# Brain regions
from unimind.regions import (
    PrefrontalCortex,
    Hippocampus,
    Amygdala,
    Cerebellum
)

# AI Models (import submodule for easy access)
from unimind import models

__all__ = [
    # Core
    "Unimind",
    "UnimindCortex",
    "get_cortex",
    
    # Neural Bus
    "NeuralBus",
    "NeuralSignal",
    "SignalType",
    "Priority",
    "get_neural_bus",
    
    # Working Memory
    "WorkingMemory",
    "ThoughtUnit",
    "Goal",
    
    # States
    "CognitiveState",
    "ConsciousnessLevel",
    
    # Decision
    "DecisionMatrix",
    
    # Brain Regions
    "PrefrontalCortex",
    "Hippocampus",
    "Amygdala",
    "Cerebellum",
    
    # AI Models Package
    "models"
]
