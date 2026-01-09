# world_engine/entities/__init__.py
"""
Entity system for the World Engine.

Provides:
- Base entity class
- Physics bodies
- Particles and particle systems
- Force field entities
"""

from world_engine.entities.entity import Entity, Transform
from world_engine.entities.body import PhysicsBody, BodyType

__all__ = [
    "Entity",
    "Transform",
    "PhysicsBody",
    "BodyType"
]
