from typing import List, Dict, Any
from world_engine.state import WorldState, Entity

class PhysicsEngine:
    def __init__(self):
        self.gravity = 9.8
    
    def update(self, state: WorldState) -> List[str]:
        logs = []
        
        for entity in state.entities.values():
            # Skip if entity has no location
            if not entity.location_id:
                continue
            
            props = entity.properties
            mass = props.get("mass", 70.0)
            velocity = props.get("velocity", [0.0, 0.0, 0.0])
            position = props.get("position", [0.0, 0.0, 0.0])
            
            # Simple Movement Integration
            # Pos = Pos + Vel * dt (assuming dt=1 for simplicity)
            new_pos = [
                position[0] + velocity[0],
                position[1] + velocity[1],
                position[2] + velocity[2]
            ]
            
            # Ground collision (simple floor at y=0)
            if new_pos[1] < 0:
                new_pos[1] = 0
                velocity[1] = 0 # Stop falling
            
            # Apply Gravity if in air
            if new_pos[1] > 0:
                velocity[1] -= self.gravity * 0.1 # scaled down for tick duration
            
            # Friction / Drag (slowing down)
            velocity[0] *= 0.9
            velocity[2] *= 0.9
            
            # Update State
            if new_pos != position:
                entity.properties["position"] = new_pos
                # Round for clean logging
                formatted_pos = [round(x, 2) for x in new_pos]
                # logs.append(f"Physics: {entity.name} moved to {formatted_pos}")
            
            entity.properties["velocity"] = velocity

        return logs

    def apply_force(self, entity: Entity, force: List[float]):
        """F = ma -> a = F/m -> dv = F/m"""
        mass = entity.properties.get("mass", 1.0)
        accel = [f / mass for f in force]
        velocity = entity.properties.get("velocity", [0.0, 0.0, 0.0])
        
        entity.properties["velocity"] = [
            velocity[0] + accel[0],
            velocity[1] + accel[1],
            velocity[2] + accel[2]
        ]
