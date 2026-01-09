# world_engine/physics/__init__.py
"""
Physics subsystem for the World Engine.

Provides:
- Force simulation (gravity, wind, custom forces)
- Constraint system (joints, springs, limits)
- Collision detection and response
- Material properties
- Narrative physics modifiers
"""

from world_engine.physics.physics_engine import PhysicsEngine
from world_engine.physics.forces import Force, ForceField, ForceType
from world_engine.physics.constraints import Constraint, ConstraintType
from world_engine.physics.materials import Material, MaterialLibrary

__all__ = [
    "PhysicsEngine",
    "Force",
    "ForceField",
    "ForceType",
    "Constraint",
    "ConstraintType",
    "Material",
    "MaterialLibrary"
]
