# world_engine/__init__.py
"""
ThothOS World Engine - AI-Native World Simulation

The world engine provides:
- Symbolic physics simulation
- Spatial indexing and collision detection
- Entity component system
- Causal rule processing
- Time flow management
- Narrative-aware physics

This is an AI-native physics engine designed for:
- Story realm simulation
- Game world generation
- Agent environment modeling
- Emergent behavior systems
"""

from world_engine.world_core import WorldEngine, WorldConfig
from world_engine.physics.physics_engine import PhysicsEngine
from world_engine.entities.entity import Entity
from world_engine.entities.body import PhysicsBody
from world_engine.time.time_manager import TimeManager

__all__ = [
    "WorldEngine",
    "WorldConfig",
    "PhysicsEngine",
    "Entity",
    "PhysicsBody",
    "TimeManager"
]

__version__ = "1.0.0"
