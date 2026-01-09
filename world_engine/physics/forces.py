# world_engine/physics/forces.py
"""
Forces - Force types and application for physics simulation.

Provides:
- Point forces (gravity, wind)
- Force fields (vortex, attractor, repulsor)
- Directional forces
- Narrative forces (fate, dramatic tension)
"""

import math
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


class ForceType(Enum):
    """Types of forces."""
    CONSTANT = auto()       # Constant force (e.g., gravity)
    LINEAR = auto()         # Linear falloff with distance
    INVERSE_SQUARE = auto() # Inverse square falloff (e.g., gravity wells)
    VORTEX = auto()         # Circular/spiral force
    NOISE = auto()          # Perlin noise-based turbulence
    DRAG = auto()           # Velocity-dependent resistance
    SPRING = auto()         # Spring-like restoring force
    CUSTOM = auto()         # Custom force function


class ForceSpace(Enum):
    """Coordinate space for forces."""
    WORLD = auto()          # World coordinates
    LOCAL = auto()          # Local to entity
    RELATIVE = auto()       # Relative to another entity


@dataclass
class Force:
    """
    A force that can be applied to physics bodies.
    
    Forces can be:
    - Global (applied to all bodies)
    - Targeted (applied to specific bodies)
    - Conditional (based on predicates)
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "force"
    force_type: ForceType = ForceType.CONSTANT
    
    # Force vector (for constant/directional forces)
    direction: Tuple[float, float, float] = (0, -1, 0)
    magnitude: float = 10.0
    
    # Falloff settings
    falloff_start: float = 0.0
    falloff_end: float = 100.0
    
    # Targeting
    target_tags: List[str] = field(default_factory=list)
    exclude_tags: List[str] = field(default_factory=list)
    target_predicate: Optional[Callable] = None
    
    # State
    enabled: bool = True
    
    # Narrative properties
    narrative_weight: float = 1.0  # How much narrative physics affects this
    
    def apply_to(self, body: 'PhysicsBody', dt: float):
        """Apply this force to a body."""
        if not self.enabled:
            return
        
        # Check targeting
        if self.target_tags:
            if not any(tag in body.entity.tags for tag in self.target_tags):
                return
        
        if self.exclude_tags:
            if any(tag in body.entity.tags for tag in self.exclude_tags):
                return
        
        if self.target_predicate and not self.target_predicate(body):
            return
        
        # Calculate force based on type
        force = self._calculate_force(body)
        
        # Apply to body
        if force:
            body.apply_force(force)
    
    def _calculate_force(self, body: 'PhysicsBody') -> Optional[Tuple[float, float, float]]:
        """Calculate the force vector for a body."""
        if self.force_type == ForceType.CONSTANT:
            return (
                self.direction[0] * self.magnitude,
                self.direction[1] * self.magnitude,
                self.direction[2] * self.magnitude
            )
        
        elif self.force_type == ForceType.DRAG:
            # Velocity-dependent drag
            speed_sq = sum(v**2 for v in body.velocity)
            if speed_sq < 0.0001:
                return None
            
            speed = math.sqrt(speed_sq)
            drag = self.magnitude * speed_sq
            
            return (
                -body.velocity[0] / speed * drag,
                -body.velocity[1] / speed * drag,
                -body.velocity[2] / speed * drag
            )
        
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """Get force information."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.force_type.name,
            "magnitude": self.magnitude,
            "enabled": self.enabled
        }


@dataclass
class ForceField:
    """
    A spatial force field that affects bodies within its bounds.
    
    Force fields have:
    - A shape (sphere, box, cylinder)
    - A center position
    - A force calculation based on position
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "field"
    force_type: ForceType = ForceType.LINEAR
    
    # Position and shape
    position: Tuple[float, float, float] = (0, 0, 0)
    radius: float = 10.0
    shape: str = "sphere"  # sphere, box, cylinder
    box_size: Tuple[float, float, float] = (10, 10, 10)
    
    # Force properties
    strength: float = 10.0
    direction: Tuple[float, float, float] = (0, 1, 0)  # For directional fields
    
    # Attractor/repulsor
    is_attractor: bool = True  # False = repulsor
    
    # Vortex properties
    vortex_axis: Tuple[float, float, float] = (0, 1, 0)
    vortex_tangent_strength: float = 5.0
    vortex_inward_strength: float = 2.0
    
    # State
    enabled: bool = True
    
    # Narrative
    narrative_tag: str = ""  # For narrative physics
    
    def contains(self, position: Tuple[float, float, float]) -> bool:
        """Check if a position is within the field."""
        if self.shape == "sphere":
            dx = position[0] - self.position[0]
            dy = position[1] - self.position[1]
            dz = position[2] - self.position[2]
            return (dx*dx + dy*dy + dz*dz) <= self.radius * self.radius
        
        elif self.shape == "box":
            half = (self.box_size[0]/2, self.box_size[1]/2, self.box_size[2]/2)
            return (
                abs(position[0] - self.position[0]) <= half[0] and
                abs(position[1] - self.position[1]) <= half[1] and
                abs(position[2] - self.position[2]) <= half[2]
            )
        
        return False
    
    def apply_to(self, body: 'PhysicsBody', dt: float):
        """Apply the field force to a body."""
        if not self.enabled:
            return
        
        force = self._calculate_force(body.position)
        if force:
            body.apply_force(force)
    
    def _calculate_force(self, position: Tuple[float, float, float]) -> Optional[Tuple[float, float, float]]:
        """Calculate force at a position."""
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        dz = position[2] - self.position[2]
        
        dist_sq = dx*dx + dy*dy + dz*dz
        dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0001
        
        if self.force_type == ForceType.CONSTANT:
            # Constant force in direction
            return (
                self.direction[0] * self.strength,
                self.direction[1] * self.strength,
                self.direction[2] * self.strength
            )
        
        elif self.force_type == ForceType.LINEAR:
            # Linear falloff attractor/repulsor
            falloff = max(0, 1 - dist / self.radius)
            magnitude = self.strength * falloff
            
            if not self.is_attractor:
                magnitude = -magnitude
            
            # Direction to/from center
            nx, ny, nz = -dx/dist, -dy/dist, -dz/dist
            
            return (nx * magnitude, ny * magnitude, nz * magnitude)
        
        elif self.force_type == ForceType.INVERSE_SQUARE:
            # Inverse square falloff (gravity-like)
            magnitude = self.strength / (dist_sq + 0.1)  # +0.1 to avoid singularity
            
            if not self.is_attractor:
                magnitude = -magnitude
            
            nx, ny, nz = -dx/dist, -dy/dist, -dz/dist
            
            return (nx * magnitude, ny * magnitude, nz * magnitude)
        
        elif self.force_type == ForceType.VORTEX:
            # Vortex/tornado force
            # Tangent force (circular motion)
            ax, ay, az = self.vortex_axis
            
            # Cross product: axis × displacement = tangent
            tx = ay * dz - az * dy
            ty = az * dx - ax * dz
            tz = ax * dy - ay * dx
            
            t_len = math.sqrt(tx*tx + ty*ty + tz*tz)
            if t_len > 0.0001:
                tx, ty, tz = tx/t_len, ty/t_len, tz/t_len
            
            # Inward force
            nx, ny, nz = -dx/dist, -dy/dist, -dz/dist
            
            falloff = max(0, 1 - dist / self.radius)
            
            return (
                (tx * self.vortex_tangent_strength + nx * self.vortex_inward_strength) * falloff,
                (ty * self.vortex_tangent_strength + ny * self.vortex_inward_strength) * falloff,
                (tz * self.vortex_tangent_strength + nz * self.vortex_inward_strength) * falloff
            )
        
        return None


class GravityWell(ForceField):
    """A gravity well attractor."""
    
    def __init__(self, position: Tuple[float, float, float], strength: float = 100.0, radius: float = 50.0):
        super().__init__(
            name="gravity_well",
            force_type=ForceType.INVERSE_SQUARE,
            position=position,
            radius=radius,
            strength=strength,
            is_attractor=True
        )


class WindZone(ForceField):
    """A wind zone with constant directional force."""
    
    def __init__(
        self,
        position: Tuple[float, float, float],
        direction: Tuple[float, float, float],
        strength: float = 5.0,
        size: Tuple[float, float, float] = (20, 20, 20)
    ):
        super().__init__(
            name="wind_zone",
            force_type=ForceType.CONSTANT,
            position=position,
            shape="box",
            box_size=size,
            direction=direction,
            strength=strength
        )


class Vortex(ForceField):
    """A vortex/tornado force field."""
    
    def __init__(
        self,
        position: Tuple[float, float, float],
        radius: float = 15.0,
        tangent_strength: float = 10.0,
        inward_strength: float = 3.0,
        axis: Tuple[float, float, float] = (0, 1, 0)
    ):
        super().__init__(
            name="vortex",
            force_type=ForceType.VORTEX,
            position=position,
            radius=radius,
            vortex_axis=axis,
            vortex_tangent_strength=tangent_strength,
            vortex_inward_strength=inward_strength
        )


class Explosion(ForceField):
    """An explosion force (radial impulse)."""
    
    def __init__(
        self,
        position: Tuple[float, float, float],
        strength: float = 500.0,
        radius: float = 20.0
    ):
        super().__init__(
            name="explosion",
            force_type=ForceType.LINEAR,
            position=position,
            radius=radius,
            strength=strength,
            is_attractor=False  # Repulsor
        )
        self.duration = 0.1  # Explosions are brief
        self.elapsed = 0.0
    
    def apply_to(self, body: 'PhysicsBody', dt: float):
        """Apply explosion force as impulse."""
        if self.elapsed >= self.duration:
            self.enabled = False
            return
        
        self.elapsed += dt
        super().apply_to(body, dt)


# Narrative Forces

class FateForce(Force):
    """
    A narrative force that guides objects toward their 'fate'.
    
    Used for dramatic moments where objects should reach
    specific destinations regardless of physics.
    """
    
    def __init__(
        self,
        target_entity_id: str,
        destination: Tuple[float, float, float],
        strength: float = 5.0,
        urgency: float = 1.0
    ):
        super().__init__(
            name="fate",
            force_type=ForceType.CUSTOM,
            magnitude=strength
        )
        self.target_entity_id = target_entity_id
        self.destination = destination
        self.urgency = urgency  # How strongly physics is overridden
    
    def apply_to(self, body: 'PhysicsBody', dt: float):
        """Apply fate force."""
        if body.entity.id != self.target_entity_id:
            return
        
        dx = self.destination[0] - body.position[0]
        dy = self.destination[1] - body.position[1]
        dz = self.destination[2] - body.position[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.1:
            self.enabled = False
            return
        
        # Force toward destination
        force_mag = self.magnitude * self.urgency
        
        body.apply_force((
            dx / dist * force_mag,
            dy / dist * force_mag,
            dz / dist * force_mag
        ))


class DramaticSlowdown:
    """
    Narrative modifier that slows time during dramatic moments.
    
    Affects the time scale of physics for specific entities
    or the entire world.
    """
    
    def __init__(
        self,
        time_scale: float = 0.2,
        duration: float = 2.0,
        affected_tags: List[str] = None
    ):
        self.time_scale = time_scale
        self.duration = duration
        self.affected_tags = affected_tags or []
        self.elapsed = 0.0
        self.enabled = True
    
    def apply(self, physics: 'PhysicsEngine', dt: float):
        """Apply dramatic slowdown."""
        if not self.enabled:
            return
        
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.enabled = False
            return
        
        # This would modify the world's time scale
        # For now, we affect individual body velocities
        for body in physics._bodies.values():
            if self.affected_tags:
                if not any(tag in body.entity.tags for tag in self.affected_tags):
                    continue
            
            # Reduce velocity temporarily
            body.velocity = (
                body.velocity[0] * self.time_scale,
                body.velocity[1] * self.time_scale,
                body.velocity[2] * self.time_scale
            )
