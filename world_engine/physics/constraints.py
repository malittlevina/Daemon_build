# world_engine/physics/constraints.py
"""
Constraints - Physical constraints for the physics simulation.

Provides:
- Distance constraints (rods, ropes)
- Angular constraints (hinges, joints)
- Position constraints (anchors, limits)
- Soft constraints (springs, dampers)
"""

import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


class ConstraintType(Enum):
    """Types of constraints."""
    DISTANCE = auto()       # Fixed distance between two bodies
    ROPE = auto()           # Maximum distance (can be shorter)
    SPRING = auto()         # Spring-like connection
    HINGE = auto()          # Rotation around an axis
    BALL = auto()           # Ball joint (3 DOF rotation)
    SLIDER = auto()         # Translation along an axis
    FIXED = auto()          # No relative motion
    POINT = auto()          # Fixed point in world
    PLANE = auto()          # Constrain to a plane
    LOOK_AT = auto()        # Orientation constraint


@dataclass
class Constraint:
    """
    Base class for physics constraints.
    
    Constraints limit the relative motion between bodies
    or between a body and the world.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "constraint"
    constraint_type: ConstraintType = ConstraintType.DISTANCE
    
    # Connected bodies (None = world)
    body_a_id: Optional[str] = None
    body_b_id: Optional[str] = None
    
    # Local attachment points
    local_anchor_a: Tuple[float, float, float] = (0, 0, 0)
    local_anchor_b: Tuple[float, float, float] = (0, 0, 0)
    
    # Constraint parameters
    stiffness: float = 1.0        # 0-1, how rigid
    damping: float = 0.3          # Velocity damping
    
    # Limits
    min_limit: float = 0.0
    max_limit: float = float('inf')
    
    # State
    enabled: bool = True
    broken: bool = False
    break_force: float = float('inf')  # Force to break constraint
    
    # Reference to physics engine (set when added)
    physics: Optional['PhysicsEngine'] = field(default=None, repr=False)
    
    def solve_velocity(self, dt: float):
        """Solve velocity constraint (override in subclasses)."""
        pass
    
    def solve_position(self, dt: float):
        """Solve position constraint (override in subclasses)."""
        pass
    
    def get_force(self) -> float:
        """Get the current force on the constraint."""
        return 0.0
    
    def check_break(self):
        """Check if constraint should break."""
        if self.get_force() > self.break_force:
            self.broken = True
            self.enabled = False


@dataclass
class DistanceConstraint(Constraint):
    """
    Maintains a fixed distance between two bodies or body and world.
    """
    
    target_distance: float = 1.0
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.DISTANCE
        self.name = "distance"
    
    def solve_velocity(self, dt: float):
        """Solve velocity to maintain distance."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body_a = self.physics.get_body(self.body_a_id) if self.body_a_id else None
        body_b = self.physics.get_body(self.body_b_id) if self.body_b_id else None
        
        if not body_a and not body_b:
            return
        
        # Get world positions of anchors
        pos_a = self._get_world_anchor(body_a, self.local_anchor_a)
        pos_b = self._get_world_anchor(body_b, self.local_anchor_b)
        
        # Direction vector
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.0001:
            return
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        
        # Relative velocity along constraint
        vel_a = body_a.velocity if body_a else (0, 0, 0)
        vel_b = body_b.velocity if body_b else (0, 0, 0)
        
        rel_vel = (
            (vel_b[0] - vel_a[0]) * nx +
            (vel_b[1] - vel_a[1]) * ny +
            (vel_b[2] - vel_a[2]) * nz
        )
        
        # Calculate impulse
        inv_mass_a = 0 if not body_a or body_a.is_static else 1.0 / body_a.mass
        inv_mass_b = 0 if not body_b or body_b.is_static else 1.0 / body_b.mass
        total_inv_mass = inv_mass_a + inv_mass_b
        
        if total_inv_mass == 0:
            return
        
        # Damping impulse
        impulse = -self.damping * rel_vel / total_inv_mass
        
        # Apply impulse
        if body_a and not body_a.is_static:
            body_a.velocity = (
                body_a.velocity[0] - impulse * inv_mass_a * nx,
                body_a.velocity[1] - impulse * inv_mass_a * ny,
                body_a.velocity[2] - impulse * inv_mass_a * nz
            )
        
        if body_b and not body_b.is_static:
            body_b.velocity = (
                body_b.velocity[0] + impulse * inv_mass_b * nx,
                body_b.velocity[1] + impulse * inv_mass_b * ny,
                body_b.velocity[2] + impulse * inv_mass_b * nz
            )
    
    def solve_position(self, dt: float):
        """Correct positions to maintain distance."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body_a = self.physics.get_body(self.body_a_id) if self.body_a_id else None
        body_b = self.physics.get_body(self.body_b_id) if self.body_b_id else None
        
        if not body_a and not body_b:
            return
        
        pos_a = self._get_world_anchor(body_a, self.local_anchor_a)
        pos_b = self._get_world_anchor(body_b, self.local_anchor_b)
        
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.0001:
            return
        
        error = dist - self.target_distance
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        
        # Position correction
        inv_mass_a = 0 if not body_a or body_a.is_static else 1.0 / body_a.mass
        inv_mass_b = 0 if not body_b or body_b.is_static else 1.0 / body_b.mass
        total_inv_mass = inv_mass_a + inv_mass_b
        
        if total_inv_mass == 0:
            return
        
        correction = error * self.stiffness
        
        if body_a and not body_a.is_static:
            ratio = inv_mass_a / total_inv_mass
            body_a.position = (
                body_a.position[0] + nx * correction * ratio,
                body_a.position[1] + ny * correction * ratio,
                body_a.position[2] + nz * correction * ratio
            )
        
        if body_b and not body_b.is_static:
            ratio = inv_mass_b / total_inv_mass
            body_b.position = (
                body_b.position[0] - nx * correction * ratio,
                body_b.position[1] - ny * correction * ratio,
                body_b.position[2] - nz * correction * ratio
            )
    
    def _get_world_anchor(self, body, local_anchor) -> Tuple[float, float, float]:
        """Get world position of anchor point."""
        if body:
            return (
                body.position[0] + local_anchor[0],
                body.position[1] + local_anchor[1],
                body.position[2] + local_anchor[2]
            )
        return local_anchor


@dataclass
class SpringConstraint(Constraint):
    """
    A spring connection between two bodies.
    """
    
    rest_length: float = 1.0
    spring_constant: float = 50.0  # Stiffness
    damping_constant: float = 5.0
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.SPRING
        self.name = "spring"
    
    def solve_velocity(self, dt: float):
        """Apply spring force."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body_a = self.physics.get_body(self.body_a_id) if self.body_a_id else None
        body_b = self.physics.get_body(self.body_b_id) if self.body_b_id else None
        
        if not body_a and not body_b:
            return
        
        pos_a = body_a.position if body_a else self.local_anchor_a
        pos_b = body_b.position if body_b else self.local_anchor_b
        
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.0001:
            return
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        
        # Spring force: F = -k * (x - rest_length)
        extension = dist - self.rest_length
        spring_force = self.spring_constant * extension
        
        # Damping force
        vel_a = body_a.velocity if body_a else (0, 0, 0)
        vel_b = body_b.velocity if body_b else (0, 0, 0)
        
        rel_vel = (
            (vel_b[0] - vel_a[0]) * nx +
            (vel_b[1] - vel_a[1]) * ny +
            (vel_b[2] - vel_a[2]) * nz
        )
        
        damping_force = self.damping_constant * rel_vel
        
        total_force = spring_force + damping_force
        
        # Apply forces
        if body_a and not body_a.is_static:
            body_a.apply_force((
                nx * total_force,
                ny * total_force,
                nz * total_force
            ))
        
        if body_b and not body_b.is_static:
            body_b.apply_force((
                -nx * total_force,
                -ny * total_force,
                -nz * total_force
            ))
    
    def solve_position(self, dt: float):
        """Springs don't need position correction."""
        pass


@dataclass
class RopeConstraint(Constraint):
    """
    A rope constraint - maximum distance only.
    Bodies can be closer but not further.
    """
    
    max_length: float = 5.0
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.ROPE
        self.name = "rope"
    
    def solve_velocity(self, dt: float):
        """Solve rope constraint."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body_a = self.physics.get_body(self.body_a_id) if self.body_a_id else None
        body_b = self.physics.get_body(self.body_b_id) if self.body_b_id else None
        
        if not body_a and not body_b:
            return
        
        pos_a = body_a.position if body_a else self.local_anchor_a
        pos_b = body_b.position if body_b else self.local_anchor_b
        
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Only constrain if stretched beyond max
        if dist <= self.max_length:
            return
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        
        # Relative velocity toward each other
        vel_a = body_a.velocity if body_a else (0, 0, 0)
        vel_b = body_b.velocity if body_b else (0, 0, 0)
        
        rel_vel = (
            (vel_b[0] - vel_a[0]) * nx +
            (vel_b[1] - vel_a[1]) * ny +
            (vel_b[2] - vel_a[2]) * nz
        )
        
        # Only constrain if moving apart
        if rel_vel <= 0:
            return
        
        inv_mass_a = 0 if not body_a or body_a.is_static else 1.0 / body_a.mass
        inv_mass_b = 0 if not body_b or body_b.is_static else 1.0 / body_b.mass
        total_inv_mass = inv_mass_a + inv_mass_b
        
        if total_inv_mass == 0:
            return
        
        impulse = rel_vel / total_inv_mass
        
        if body_a and not body_a.is_static:
            body_a.velocity = (
                body_a.velocity[0] + impulse * inv_mass_a * nx,
                body_a.velocity[1] + impulse * inv_mass_a * ny,
                body_a.velocity[2] + impulse * inv_mass_a * nz
            )
        
        if body_b and not body_b.is_static:
            body_b.velocity = (
                body_b.velocity[0] - impulse * inv_mass_b * nx,
                body_b.velocity[1] - impulse * inv_mass_b * ny,
                body_b.velocity[2] - impulse * inv_mass_b * nz
            )
    
    def solve_position(self, dt: float):
        """Correct positions if beyond max length."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body_a = self.physics.get_body(self.body_a_id) if self.body_a_id else None
        body_b = self.physics.get_body(self.body_b_id) if self.body_b_id else None
        
        if not body_a and not body_b:
            return
        
        pos_a = body_a.position if body_a else self.local_anchor_a
        pos_b = body_b.position if body_b else self.local_anchor_b
        
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist <= self.max_length:
            return
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        error = dist - self.max_length
        
        inv_mass_a = 0 if not body_a or body_a.is_static else 1.0 / body_a.mass
        inv_mass_b = 0 if not body_b or body_b.is_static else 1.0 / body_b.mass
        total_inv_mass = inv_mass_a + inv_mass_b
        
        if total_inv_mass == 0:
            return
        
        if body_a and not body_a.is_static:
            ratio = inv_mass_a / total_inv_mass
            body_a.position = (
                body_a.position[0] + nx * error * ratio,
                body_a.position[1] + ny * error * ratio,
                body_a.position[2] + nz * error * ratio
            )
        
        if body_b and not body_b.is_static:
            ratio = inv_mass_b / total_inv_mass
            body_b.position = (
                body_b.position[0] - nx * error * ratio,
                body_b.position[1] - ny * error * ratio,
                body_b.position[2] - nz * error * ratio
            )


@dataclass
class PointConstraint(Constraint):
    """
    Constrains a body to a fixed point in world space.
    Like nailing something to the wall.
    """
    
    world_point: Tuple[float, float, float] = (0, 0, 0)
    
    def __post_init__(self):
        self.constraint_type = ConstraintType.POINT
        self.name = "point"
    
    def solve_velocity(self, dt: float):
        """Stop velocity toward/away from point."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body = self.physics.get_body(self.body_a_id)
        if not body or body.is_static:
            return
        
        # Zero out velocity
        body.velocity = (0, 0, 0)
    
    def solve_position(self, dt: float):
        """Snap to point."""
        if not self.enabled or self.broken or not self.physics:
            return
        
        body = self.physics.get_body(self.body_a_id)
        if not body or body.is_static:
            return
        
        target = (
            self.world_point[0] + self.local_anchor_a[0],
            self.world_point[1] + self.local_anchor_a[1],
            self.world_point[2] + self.local_anchor_a[2]
        )
        
        body.position = target
