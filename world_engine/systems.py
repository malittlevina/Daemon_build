from world_engine.ecs import System
from world_engine.components import Transform, Velocity, Script

class MovementSystem(System):
    def update(self, delta_time: float):
        # Move entities that have Transform and Velocity
        entities = self.world.entity_manager.get_entities_with(Transform, Velocity)
        for entity in entities:
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)
            
            # Euler integration
            transform.position[0] += velocity.vector[0] * delta_time
            transform.position[1] += velocity.vector[1] * delta_time
            transform.position[2] += velocity.vector[2] * delta_time

class ScriptSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Script)
        for entity in entities:
            script = entity.get_component(Script)
            # Dangerous in production, but suitable for this prototype
            # We execute the script in a constrained local scope
            try:
                local_scope = {"entity": entity, "dt": delta_time, "state": script.state, "print": print}
                exec(script.source_code, {}, local_scope)
            except Exception as e:
                print(f"[ScriptSystem] Error in entity {entity.uid}: {e}")

class PhysicsSystem(System):
    """Stub for future physics engine integration (Bullet/Jolt)."""
    def update(self, delta_time: float):
        pass
