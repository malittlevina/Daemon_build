from world_engine.ecs import System
from world_engine.components import Transform, Velocity, Script, Collider, Name

class MovementSystem(System):
    def update(self, delta_time: float):
        # Move entities that have Transform and Velocity
        entities = self.world.entity_manager.get_entities_with(Transform, Velocity)
        for entity in entities:
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)
            
            # Simple Euler integration
            transform.position[0] += velocity.vector[0] * delta_time
            transform.position[1] += velocity.vector[1] * delta_time
            transform.position[2] += velocity.vector[2] * delta_time

class CollisionSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Transform, Collider)
        
        # Reset collisions
        for e in entities:
            e.get_component(Collider).collisions = []

        # Brute force O(N^2) check (Optimization needed later: Octree)
        count = len(entities)
        for i in range(count):
            e1 = entities[i]
            t1 = e1.get_component(Transform)
            c1 = e1.get_component(Collider)
            
            for j in range(i + 1, count):
                e2 = entities[j]
                t2 = e2.get_component(Transform)
                c2 = e2.get_component(Collider)

                if self._check_aabb(t1, c1, t2, c2):
                    # Register Collision
                    c1.collisions.append(e2.uid)
                    c2.collisions.append(e1.uid)
                    
                    # Resolve Physics (simple bounce/stop) if not triggers
                    if not c1.is_trigger and not c2.is_trigger:
                        self._resolve_collision(e1, e2)
                        
                    # Log event
                    # print(f"[Collision] {e1.uid} hit {e2.uid}")

    def _check_aabb(self, t1, c1, t2, c2):
        # Calculate bounds
        min1 = [t1.position[k] - c1.size[k]/2 for k in range(3)]
        max1 = [t1.position[k] + c1.size[k]/2 for k in range(3)]
        
        min2 = [t2.position[k] - c2.size[k]/2 for k in range(3)]
        max2 = [t2.position[k] + c2.size[k]/2 for k in range(3)]
        
        return (min1[0] <= max2[0] and max1[0] >= min2[0] and
                min1[1] <= max2[1] and max1[1] >= min2[1] and
                min1[2] <= max2[2] and max1[2] >= min2[2])

    def _resolve_collision(self, e1, e2):
        # Very basic resolution: stop velocity
        v1 = e1.get_component(Velocity)
        v2 = e2.get_component(Velocity)
        
        if v1: v1.vector = [0.0, 0.0, 0.0]
        if v2: v2.vector = [0.0, 0.0, 0.0]

class ScriptSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Script)
        for entity in entities:
            script = entity.get_component(Script)
            try:
                # Inject useful context
                name = entity.get_component(Name).name if entity.get_component(Name) else "Unknown"
                collisions = entity.get_component(Collider).collisions if entity.has_component(Collider) else []
                
                local_scope = {
                    "entity": entity, 
                    "dt": delta_time, 
                    "state": script.state, 
                    "print": print,
                    "name": name,
                    "collisions": collisions
                }
                exec(script.source_code, {}, local_scope)
            except Exception as e:
                print(f"[ScriptSystem] Error in entity {entity.uid}: {e}")

class PhysicsSystem(System):
    """Stub for future advanced physics."""
    def update(self, delta_time: float):
        pass
