# world_engine/physics/physics_engine.py
"""
Physics Engine - Core physics simulation for the world.

Implements:
- Rigid body dynamics
- Force integration
- Constraint solving
- Collision detection and response
- Narrative physics modifiers
"""

import math
from typing import Dict, Any, Optional, List, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


class IntegrationMethod(Enum):
    """Physics integration methods."""
    EULER = auto()           # Simple Euler (fast, less accurate)
    VERLET = auto()          # Verlet integration (stable)
    RK4 = auto()             # Runge-Kutta 4 (accurate, slower)


@dataclass
class PhysicsConfig:
    """Physics engine configuration."""
    integration_method: IntegrationMethod = IntegrationMethod.VERLET
    substeps: int = 4                    # Physics substeps per tick
    velocity_iterations: int = 8         # Constraint solver iterations
    position_iterations: int = 3         # Position correction iterations
    
    # Physics parameters
    gravity: Tuple[float, float, float] = (0, -9.81, 0)
    air_density: float = 1.225           # kg/m³
    default_friction: float = 0.5
    default_restitution: float = 0.3     # Bounciness
    
    # Limits
    max_velocity: float = 1000.0
    max_angular_velocity: float = 100.0
    sleep_threshold: float = 0.01        # Velocity below which objects sleep
    
    # Collision
    collision_margin: float = 0.01
    continuous_collision: bool = True    # CCD for fast objects


class PhysicsEngine:
    """
    The physics simulation engine.
    
    Handles:
    - Body simulation (position, velocity, forces)
    - Force application (gravity, fields, impulses)
    - Constraint solving (joints, limits)
    - Collision detection and response
    - Narrative physics (dramatic timing, fate)
    """
    
    def __init__(self, world, config: PhysicsConfig = None):
        """Initialize the physics engine."""
        self.world = world
        self.config = config or PhysicsConfig()
        
        # Override gravity from world config if set
        if world.config.gravity:
            self.config.gravity = world.config.gravity
        
        # Physics bodies (subset of entities that have physics)
        self._bodies: Dict[str, 'PhysicsBody'] = {}
        
        # Forces and fields
        self._global_forces: List['Force'] = []
        self._force_fields: List['ForceField'] = []
        
        # Constraints
        self._constraints: List['Constraint'] = []
        
        # Collision system
        self._collision_pairs: Set[Tuple[str, str]] = set()
        self._collision_callbacks: Dict[str, List[Callable]] = {}
        
        # Narrative physics modifiers
        self._narrative_modifiers: List['NarrativeModifier'] = []
        
        # Sleeping bodies (optimization)
        self._sleeping: Set[str] = set()
        
        print("[PhysicsEngine] Initialized")
    
    # =========================================================================
    # Body management
    # =========================================================================
    
    def register_body(self, body: 'PhysicsBody'):
        """Register a physics body."""
        self._bodies[body.entity.id] = body
        self.world.stats.entity_count = len(self._bodies)
    
    def unregister_body(self, entity_id: str):
        """Unregister a physics body."""
        self._bodies.pop(entity_id, None)
        self._sleeping.discard(entity_id)
    
    def get_body(self, entity_id: str) -> Optional['PhysicsBody']:
        """Get a physics body by entity ID."""
        return self._bodies.get(entity_id)
    
    # =========================================================================
    # Force management
    # =========================================================================
    
    def add_global_force(self, force: 'Force'):
        """Add a global force (applied to all bodies)."""
        self._global_forces.append(force)
        self.world.stats.active_forces += 1
    
    def remove_global_force(self, force: 'Force'):
        """Remove a global force."""
        if force in self._global_forces:
            self._global_forces.remove(force)
            self.world.stats.active_forces -= 1
    
    def add_force_field(self, field: 'ForceField'):
        """Add a force field."""
        self._force_fields.append(field)
        self.world.stats.active_forces += 1
    
    def remove_force_field(self, field: 'ForceField'):
        """Remove a force field."""
        if field in self._force_fields:
            self._force_fields.remove(field)
            self.world.stats.active_forces -= 1
    
    # =========================================================================
    # Constraint management
    # =========================================================================
    
    def add_constraint(self, constraint: 'Constraint'):
        """Add a physics constraint."""
        self._constraints.append(constraint)
        self.world.stats.active_constraints += 1
    
    def remove_constraint(self, constraint: 'Constraint'):
        """Remove a physics constraint."""
        if constraint in self._constraints:
            self._constraints.remove(constraint)
            self.world.stats.active_constraints -= 1
    
    # =========================================================================
    # Simulation step
    # =========================================================================
    
    def step(self, dt: float):
        """Run one physics simulation step."""
        if not self._bodies:
            return
        
        # Substep for stability
        substep_dt = dt / self.config.substeps
        
        for _ in range(self.config.substeps):
            self._substep(substep_dt)
    
    def _substep(self, dt: float):
        """Execute one physics substep."""
        # 1. Apply forces
        self._apply_forces(dt)
        
        # 2. Integrate velocities
        self._integrate_velocities(dt)
        
        # 3. Detect collisions
        if self.world.config.enable_collision:
            self._detect_collisions()
        
        # 4. Solve constraints
        self._solve_constraints(dt)
        
        # 5. Integrate positions
        self._integrate_positions(dt)
        
        # 6. Apply narrative modifiers
        if self.world.config.enable_narrative_physics:
            self._apply_narrative_physics(dt)
        
        # 7. Update sleeping state
        self._update_sleeping()
    
    def _apply_forces(self, dt: float):
        """Apply all forces to bodies."""
        gravity = self.config.gravity
        
        for body in self._bodies.values():
            if body.is_static or body.entity.id in self._sleeping:
                continue
            
            # Reset acceleration
            body.acceleration = (0, 0, 0)
            
            # Apply gravity
            if body.use_gravity:
                body.apply_force((
                    gravity[0] * body.mass,
                    gravity[1] * body.mass,
                    gravity[2] * body.mass
                ))
            
            # Apply global forces
            for force in self._global_forces:
                if force.enabled:
                    force.apply_to(body, dt)
            
            # Apply force fields
            for field in self._force_fields:
                if field.contains(body.position):
                    field.apply_to(body, dt)
            
            # Apply drag
            self._apply_drag(body, dt)
    
    def _apply_drag(self, body: 'PhysicsBody', dt: float):
        """Apply air resistance to a body."""
        if body.drag == 0:
            return
        
        speed_sq = (
            body.velocity[0]**2 +
            body.velocity[1]**2 +
            body.velocity[2]**2
        )
        
        if speed_sq < 0.0001:
            return
        
        speed = math.sqrt(speed_sq)
        drag_magnitude = 0.5 * self.config.air_density * speed_sq * body.drag
        
        # Apply drag force opposite to velocity
        body.apply_force((
            -body.velocity[0] / speed * drag_magnitude,
            -body.velocity[1] / speed * drag_magnitude,
            -body.velocity[2] / speed * drag_magnitude
        ))
    
    def _integrate_velocities(self, dt: float):
        """Integrate forces to velocities."""
        max_vel = self.config.max_velocity
        
        for body in self._bodies.values():
            if body.is_static or body.entity.id in self._sleeping:
                continue
            
            # v = v + a * dt
            body.velocity = (
                body.velocity[0] + body.acceleration[0] * dt,
                body.velocity[1] + body.acceleration[1] * dt,
                body.velocity[2] + body.acceleration[2] * dt
            )
            
            # Clamp velocity
            speed_sq = sum(v**2 for v in body.velocity)
            if speed_sq > max_vel**2:
                speed = math.sqrt(speed_sq)
                body.velocity = tuple(v / speed * max_vel for v in body.velocity)
    
    def _detect_collisions(self):
        """Detect collisions between bodies."""
        self._collision_pairs.clear()
        self.world.stats.collision_checks = 0
        
        # Broad phase: get potential pairs from spatial index
        potential_pairs = self.world.spatial.get_collision_pairs()
        
        for id1, id2 in potential_pairs:
            self.world.stats.collision_checks += 1
            
            body1 = self._bodies.get(id1)
            body2 = self._bodies.get(id2)
            
            if not body1 or not body2:
                continue
            
            # Skip if both static
            if body1.is_static and body2.is_static:
                continue
            
            # Narrow phase: precise collision check
            if self._check_collision(body1, body2):
                self._collision_pairs.add((id1, id2))
        
        self.world.stats.collision_pairs = len(self._collision_pairs)
    
    def _check_collision(self, body1: 'PhysicsBody', body2: 'PhysicsBody') -> bool:
        """Check precise collision between two bodies."""
        # Simple sphere-sphere collision for now
        dx = body2.position[0] - body1.position[0]
        dy = body2.position[1] - body1.position[1]
        dz = body2.position[2] - body1.position[2]
        
        dist_sq = dx*dx + dy*dy + dz*dz
        min_dist = body1.radius + body2.radius + self.config.collision_margin
        
        return dist_sq < min_dist * min_dist
    
    def _solve_constraints(self, dt: float):
        """Solve physics constraints."""
        # Velocity iterations
        for _ in range(self.config.velocity_iterations):
            # Solve collision responses
            for id1, id2 in self._collision_pairs:
                self._resolve_collision(id1, id2)
            
            # Solve other constraints
            for constraint in self._constraints:
                constraint.solve_velocity(dt)
        
        # Position iterations
        for _ in range(self.config.position_iterations):
            for id1, id2 in self._collision_pairs:
                self._correct_positions(id1, id2)
            
            for constraint in self._constraints:
                constraint.solve_position(dt)
    
    def _resolve_collision(self, id1: str, id2: str):
        """Resolve collision between two bodies."""
        body1 = self._bodies.get(id1)
        body2 = self._bodies.get(id2)
        
        if not body1 or not body2:
            return
        
        # Calculate collision normal
        dx = body2.position[0] - body1.position[0]
        dy = body2.position[1] - body1.position[1]
        dz = body2.position[2] - body1.position[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.0001:
            return
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        
        # Relative velocity
        rvx = body2.velocity[0] - body1.velocity[0]
        rvy = body2.velocity[1] - body1.velocity[1]
        rvz = body2.velocity[2] - body1.velocity[2]
        
        # Relative velocity along normal
        rv_normal = rvx*nx + rvy*ny + rvz*nz
        
        # Don't resolve if separating
        if rv_normal > 0:
            return
        
        # Calculate restitution (bounciness)
        e = min(body1.restitution, body2.restitution)
        
        # Calculate impulse magnitude
        inv_mass1 = 0 if body1.is_static else 1.0 / body1.mass
        inv_mass2 = 0 if body2.is_static else 1.0 / body2.mass
        
        j = -(1 + e) * rv_normal / (inv_mass1 + inv_mass2)
        
        # Apply impulse
        if not body1.is_static:
            body1.velocity = (
                body1.velocity[0] - j * inv_mass1 * nx,
                body1.velocity[1] - j * inv_mass1 * ny,
                body1.velocity[2] - j * inv_mass1 * nz
            )
        
        if not body2.is_static:
            body2.velocity = (
                body2.velocity[0] + j * inv_mass2 * nx,
                body2.velocity[1] + j * inv_mass2 * ny,
                body2.velocity[2] + j * inv_mass2 * nz
            )
        
        # Fire collision callbacks
        self._fire_collision_callbacks(body1.entity, body2.entity)
    
    def _correct_positions(self, id1: str, id2: str):
        """Correct penetrating positions."""
        body1 = self._bodies.get(id1)
        body2 = self._bodies.get(id2)
        
        if not body1 or not body2:
            return
        
        dx = body2.position[0] - body1.position[0]
        dy = body2.position[1] - body1.position[1]
        dz = body2.position[2] - body1.position[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        min_dist = body1.radius + body2.radius
        
        if dist >= min_dist:
            return
        
        penetration = min_dist - dist
        if dist < 0.0001:
            return
        
        nx, ny, nz = dx/dist, dy/dist, dz/dist
        
        # Correction amount
        correction = penetration * 0.8  # Baumgarte stabilization
        
        inv_mass1 = 0 if body1.is_static else 1.0 / body1.mass
        inv_mass2 = 0 if body2.is_static else 1.0 / body2.mass
        total_inv = inv_mass1 + inv_mass2
        
        if total_inv == 0:
            return
        
        # Apply position correction
        if not body1.is_static:
            ratio1 = inv_mass1 / total_inv
            body1.position = (
                body1.position[0] - nx * correction * ratio1,
                body1.position[1] - ny * correction * ratio1,
                body1.position[2] - nz * correction * ratio1
            )
        
        if not body2.is_static:
            ratio2 = inv_mass2 / total_inv
            body2.position = (
                body2.position[0] + nx * correction * ratio2,
                body2.position[1] + ny * correction * ratio2,
                body2.position[2] + nz * correction * ratio2
            )
    
    def _integrate_positions(self, dt: float):
        """Integrate velocities to positions."""
        for body in self._bodies.values():
            if body.is_static or body.entity.id in self._sleeping:
                continue
            
            # p = p + v * dt
            body.position = (
                body.position[0] + body.velocity[0] * dt,
                body.position[1] + body.velocity[1] * dt,
                body.position[2] + body.velocity[2] * dt
            )
            
            # Sync with entity transform
            body.entity.transform.position = body.position
            
            # Update spatial index
            self.world.spatial.update(body.entity)
    
    def _apply_narrative_physics(self, dt: float):
        """Apply narrative physics modifiers."""
        for modifier in self._narrative_modifiers:
            modifier.apply(self, dt)
    
    def _update_sleeping(self):
        """Update which bodies are sleeping."""
        threshold = self.config.sleep_threshold
        
        for entity_id, body in self._bodies.items():
            if body.is_static:
                continue
            
            speed_sq = sum(v**2 for v in body.velocity)
            
            if speed_sq < threshold * threshold:
                self._sleeping.add(entity_id)
            else:
                self._sleeping.discard(entity_id)
    
    # =========================================================================
    # Collision callbacks
    # =========================================================================
    
    def on_collision(self, entity_id: str, callback: Callable):
        """Register a collision callback for an entity."""
        if entity_id not in self._collision_callbacks:
            self._collision_callbacks[entity_id] = []
        self._collision_callbacks[entity_id].append(callback)
    
    def _fire_collision_callbacks(self, entity1: 'Entity', entity2: 'Entity'):
        """Fire collision callbacks."""
        for callback in self._collision_callbacks.get(entity1.id, []):
            callback(entity1, entity2)
        for callback in self._collision_callbacks.get(entity2.id, []):
            callback(entity2, entity1)
    
    # =========================================================================
    # Narrative physics
    # =========================================================================
    
    def add_narrative_modifier(self, modifier: 'NarrativeModifier'):
        """Add a narrative physics modifier."""
        self._narrative_modifiers.append(modifier)
    
    def remove_narrative_modifier(self, modifier: 'NarrativeModifier'):
        """Remove a narrative physics modifier."""
        if modifier in self._narrative_modifiers:
            self._narrative_modifiers.remove(modifier)
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def apply_impulse(self, entity_id: str, impulse: Tuple[float, float, float]):
        """Apply an instant impulse to a body."""
        body = self._bodies.get(entity_id)
        if body and not body.is_static:
            body.velocity = (
                body.velocity[0] + impulse[0] / body.mass,
                body.velocity[1] + impulse[1] / body.mass,
                body.velocity[2] + impulse[2] / body.mass
            )
            self._sleeping.discard(entity_id)
    
    def apply_force_at(self, entity_id: str, force: Tuple[float, float, float]):
        """Apply a force to a body."""
        body = self._bodies.get(entity_id)
        if body and not body.is_static:
            body.apply_force(force)
            self._sleeping.discard(entity_id)
    
    def set_velocity(self, entity_id: str, velocity: Tuple[float, float, float]):
        """Set a body's velocity directly."""
        body = self._bodies.get(entity_id)
        if body and not body.is_static:
            body.velocity = velocity
            self._sleeping.discard(entity_id)
    
    def wake(self, entity_id: str):
        """Wake a sleeping body."""
        self._sleeping.discard(entity_id)
    
    def sleep(self, entity_id: str):
        """Force a body to sleep."""
        self._sleeping.add(entity_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get physics engine statistics."""
        return {
            "body_count": len(self._bodies),
            "sleeping_count": len(self._sleeping),
            "force_count": len(self._global_forces) + len(self._force_fields),
            "constraint_count": len(self._constraints),
            "collision_pairs": len(self._collision_pairs),
            "narrative_modifiers": len(self._narrative_modifiers)
        }
