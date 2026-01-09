# world_engine/entities/body.py
"""
Physics Body - Entity with physics simulation.

A PhysicsBody is an entity that participates in physics simulation:
- Has mass and inertia
- Responds to forces
- Collides with other bodies
"""

import math
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid

from world_engine.entities.entity import Entity, Transform
from world_engine.physics.materials import Material, MaterialLibrary

if TYPE_CHECKING:
    from world_engine.world_core import WorldEngine


class BodyType(Enum):
    """Types of physics bodies."""
    DYNAMIC = auto()      # Fully simulated
    KINEMATIC = auto()    # Moved by code, affects others
    STATIC = auto()       # Never moves
    TRIGGER = auto()      # No physics, just detects overlaps


class ColliderShape(Enum):
    """Collision shape types."""
    SPHERE = auto()
    BOX = auto()
    CAPSULE = auto()
    CYLINDER = auto()
    MESH = auto()
    COMPOUND = auto()


@dataclass
class PhysicsBody:
    """
    A physics-enabled entity.
    
    Contains all physics state:
    - Position, velocity, acceleration
    - Mass and inertia
    - Forces and torques
    - Collision shape
    - Material properties
    """
    
    # Reference to entity
    entity: Entity = None
    
    # Body type
    body_type: BodyType = BodyType.DYNAMIC
    
    # Mass properties
    mass: float = 1.0
    inverse_mass: float = 1.0
    inertia: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    center_of_mass: Tuple[float, float, float] = (0, 0, 0)
    
    # Linear motion
    velocity: Tuple[float, float, float] = (0, 0, 0)
    acceleration: Tuple[float, float, float] = (0, 0, 0)
    
    # Angular motion
    angular_velocity: Tuple[float, float, float] = (0, 0, 0)
    torque: Tuple[float, float, float] = (0, 0, 0)
    
    # Forces accumulated this frame
    _force_accumulator: Tuple[float, float, float] = field(default=(0, 0, 0), repr=False)
    
    # Collision
    collider_shape: ColliderShape = ColliderShape.SPHERE
    radius: float = 0.5           # For sphere
    half_extents: Tuple[float, float, float] = (0.5, 0.5, 0.5)  # For box
    height: float = 1.0           # For capsule/cylinder
    
    # Material
    material: Material = None
    
    # Shortcuts for material properties
    friction: float = 0.5
    restitution: float = 0.3
    drag: float = 0.01
    angular_drag: float = 0.05
    
    # Flags
    use_gravity: bool = True
    is_trigger: bool = False
    continuous_collision: bool = False  # CCD for fast objects
    
    # Sleep state
    can_sleep: bool = True
    is_sleeping: bool = False
    
    # Collision filtering
    collision_layer: int = 1
    collision_mask: int = 0xFFFFFFFF  # Collide with all layers
    
    # Narrative properties
    narrative_immunity: float = 0.0   # 0-1, how much physics can be overridden
    fate_destination: Optional[Tuple[float, float, float]] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.mass > 0:
            self.inverse_mass = 1.0 / self.mass
        else:
            self.inverse_mass = 0
        
        if self.material is None:
            self.material = MaterialLibrary.get("default") or Material()
        
        # Copy material properties
        self.friction = self.material.friction
        self.restitution = self.material.restitution
    
    @property
    def position(self) -> Tuple[float, float, float]:
        """Get position from entity transform."""
        if self.entity:
            return self.entity.transform.position
        return (0, 0, 0)
    
    @position.setter
    def position(self, value: Tuple[float, float, float]):
        """Set position on entity transform."""
        if self.entity:
            self.entity.transform.position = value
    
    @property
    def rotation(self) -> Tuple[float, float, float, float]:
        """Get rotation quaternion from entity transform."""
        if self.entity:
            return self.entity.transform.rotation
        return (0, 0, 0, 1)
    
    @rotation.setter
    def rotation(self, value: Tuple[float, float, float, float]):
        """Set rotation on entity transform."""
        if self.entity:
            self.entity.transform.rotation = value
    
    @property
    def is_static(self) -> bool:
        """Check if body is static."""
        return self.body_type == BodyType.STATIC
    
    @property
    def is_kinematic(self) -> bool:
        """Check if body is kinematic."""
        return self.body_type == BodyType.KINEMATIC
    
    @property
    def is_dynamic(self) -> bool:
        """Check if body is dynamic."""
        return self.body_type == BodyType.DYNAMIC
    
    # =========================================================================
    # Force application
    # =========================================================================
    
    def apply_force(self, force: Tuple[float, float, float]):
        """Apply a force at center of mass."""
        if self.is_static or self.mass == 0:
            return
        
        # Accumulate force
        self._force_accumulator = (
            self._force_accumulator[0] + force[0],
            self._force_accumulator[1] + force[1],
            self._force_accumulator[2] + force[2]
        )
        
        # Convert to acceleration (F = ma, a = F/m)
        self.acceleration = (
            self.acceleration[0] + force[0] * self.inverse_mass,
            self.acceleration[1] + force[1] * self.inverse_mass,
            self.acceleration[2] + force[2] * self.inverse_mass
        )
    
    def apply_force_at_point(
        self,
        force: Tuple[float, float, float],
        point: Tuple[float, float, float]
    ):
        """Apply force at a world point (generates torque)."""
        self.apply_force(force)
        
        # Calculate torque: τ = r × F
        r = (
            point[0] - self.position[0],
            point[1] - self.position[1],
            point[2] - self.position[2]
        )
        
        torque = (
            r[1] * force[2] - r[2] * force[1],
            r[2] * force[0] - r[0] * force[2],
            r[0] * force[1] - r[1] * force[0]
        )
        
        self.apply_torque(torque)
    
    def apply_impulse(self, impulse: Tuple[float, float, float]):
        """Apply instant velocity change."""
        if self.is_static or self.mass == 0:
            return
        
        self.velocity = (
            self.velocity[0] + impulse[0] * self.inverse_mass,
            self.velocity[1] + impulse[1] * self.inverse_mass,
            self.velocity[2] + impulse[2] * self.inverse_mass
        )
        
        self.wake()
    
    def apply_impulse_at_point(
        self,
        impulse: Tuple[float, float, float],
        point: Tuple[float, float, float]
    ):
        """Apply impulse at a world point."""
        self.apply_impulse(impulse)
        
        # Angular impulse
        r = (
            point[0] - self.position[0],
            point[1] - self.position[1],
            point[2] - self.position[2]
        )
        
        angular_impulse = (
            r[1] * impulse[2] - r[2] * impulse[1],
            r[2] * impulse[0] - r[0] * impulse[2],
            r[0] * impulse[1] - r[1] * impulse[0]
        )
        
        self.apply_angular_impulse(angular_impulse)
    
    def apply_torque(self, torque: Tuple[float, float, float]):
        """Apply a torque."""
        if self.is_static:
            return
        
        self.torque = (
            self.torque[0] + torque[0],
            self.torque[1] + torque[1],
            self.torque[2] + torque[2]
        )
    
    def apply_angular_impulse(self, impulse: Tuple[float, float, float]):
        """Apply angular impulse."""
        if self.is_static:
            return
        
        self.angular_velocity = (
            self.angular_velocity[0] + impulse[0] / self.inertia[0],
            self.angular_velocity[1] + impulse[1] / self.inertia[1],
            self.angular_velocity[2] + impulse[2] / self.inertia[2]
        )
        
        self.wake()
    
    def clear_forces(self):
        """Clear accumulated forces."""
        self._force_accumulator = (0, 0, 0)
        self.acceleration = (0, 0, 0)
        self.torque = (0, 0, 0)
    
    # =========================================================================
    # Velocity
    # =========================================================================
    
    def set_velocity(self, velocity: Tuple[float, float, float]):
        """Set linear velocity."""
        self.velocity = velocity
        self.wake()
    
    def add_velocity(self, delta: Tuple[float, float, float]):
        """Add to velocity."""
        self.velocity = (
            self.velocity[0] + delta[0],
            self.velocity[1] + delta[1],
            self.velocity[2] + delta[2]
        )
        self.wake()
    
    def get_speed(self) -> float:
        """Get current speed."""
        return math.sqrt(
            self.velocity[0]**2 +
            self.velocity[1]**2 +
            self.velocity[2]**2
        )
    
    def get_velocity_at_point(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Get velocity at a world point (includes angular velocity)."""
        r = (
            point[0] - self.position[0],
            point[1] - self.position[1],
            point[2] - self.position[2]
        )
        
        # v = v_linear + ω × r
        angular_contribution = (
            self.angular_velocity[1] * r[2] - self.angular_velocity[2] * r[1],
            self.angular_velocity[2] * r[0] - self.angular_velocity[0] * r[2],
            self.angular_velocity[0] * r[1] - self.angular_velocity[1] * r[0]
        )
        
        return (
            self.velocity[0] + angular_contribution[0],
            self.velocity[1] + angular_contribution[1],
            self.velocity[2] + angular_contribution[2]
        )
    
    # =========================================================================
    # Sleep
    # =========================================================================
    
    def wake(self):
        """Wake the body from sleep."""
        self.is_sleeping = False
    
    def sleep(self):
        """Put the body to sleep."""
        if self.can_sleep:
            self.is_sleeping = True
            self.velocity = (0, 0, 0)
            self.angular_velocity = (0, 0, 0)
    
    # =========================================================================
    # Collision
    # =========================================================================
    
    def get_bounding_sphere_radius(self) -> float:
        """Get bounding sphere radius for broad phase."""
        if self.collider_shape == ColliderShape.SPHERE:
            return self.radius
        elif self.collider_shape == ColliderShape.BOX:
            return math.sqrt(
                self.half_extents[0]**2 +
                self.half_extents[1]**2 +
                self.half_extents[2]**2
            )
        elif self.collider_shape in (ColliderShape.CAPSULE, ColliderShape.CYLINDER):
            return max(self.radius, self.height / 2)
        return self.radius
    
    def get_aabb(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Get axis-aligned bounding box."""
        r = self.get_bounding_sphere_radius()
        pos = self.position
        return (
            (pos[0] - r, pos[1] - r, pos[2] - r),
            (pos[0] + r, pos[1] + r, pos[2] + r)
        )
    
    def can_collide_with(self, other: 'PhysicsBody') -> bool:
        """Check if this body can collide with another."""
        # Check layer mask
        if not (self.collision_mask & (1 << other.collision_layer)):
            return False
        if not (other.collision_mask & (1 << self.collision_layer)):
            return False
        return True
    
    # =========================================================================
    # Narrative
    # =========================================================================
    
    def set_fate(self, destination: Tuple[float, float, float], urgency: float = 0.5):
        """Set a narrative fate destination."""
        self.fate_destination = destination
        self.narrative_immunity = urgency
    
    def clear_fate(self):
        """Clear narrative fate."""
        self.fate_destination = None
        self.narrative_immunity = 0.0
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entity_id": self.entity.id if self.entity else None,
            "body_type": self.body_type.name,
            "mass": self.mass,
            "velocity": self.velocity,
            "angular_velocity": self.angular_velocity,
            "collider_shape": self.collider_shape.name,
            "radius": self.radius,
            "half_extents": self.half_extents,
            "material": self.material.name if self.material else None,
            "use_gravity": self.use_gravity,
            "collision_layer": self.collision_layer,
            "collision_mask": self.collision_mask
        }


def create_physics_entity(
    name: str = "physics_object",
    position: Tuple[float, float, float] = (0, 0, 0),
    mass: float = 1.0,
    radius: float = 0.5,
    material: str = "default",
    body_type: BodyType = BodyType.DYNAMIC,
    tags: List[str] = None
) -> Tuple[Entity, PhysicsBody]:
    """
    Convenience function to create an entity with physics body.
    """
    entity = Entity(name=name, tags=set(tags or []))
    entity.transform.position = position
    
    mat = MaterialLibrary.get(material) or Material()
    
    body = PhysicsBody(
        entity=entity,
        body_type=body_type,
        mass=mass,
        radius=radius,
        material=mat
    )
    
    entity.add_component("physics", body)
    
    return entity, body
