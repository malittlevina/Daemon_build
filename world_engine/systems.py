from world_engine.ecs import System
from world_engine.components import Transform, Velocity, Script, Collider, Name, SemanticMaterial

class MovementSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Transform, Velocity)
        for entity in entities:
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)
            transform.position[0] += velocity.vector[0] * delta_time
            transform.position[1] += velocity.vector[1] * delta_time
            transform.position[2] += velocity.vector[2] * delta_time

class CollisionSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Transform, Collider)
        for e in entities: e.get_component(Collider).collisions = []
        count = len(entities)
        for i in range(count):
            e1 = entities[i]
            for j in range(i + 1, count):
                e2 = entities[j]
                if self._check_aabb(e1.get_component(Transform), e1.get_component(Collider),
                                    e2.get_component(Transform), e2.get_component(Collider)):
                    e1.get_component(Collider).collisions.append(e2.uid)
                    e2.get_component(Collider).collisions.append(e1.uid)
                    if not e1.get_component(Collider).is_trigger and not e2.get_component(Collider).is_trigger:
                        self._resolve_collision(e1, e2)

    def _check_aabb(self, t1, c1, t2, c2):
        min1 = [t1.position[k] - c1.size[k]/2 for k in range(3)]
        max1 = [t1.position[k] + c1.size[k]/2 for k in range(3)]
        min2 = [t2.position[k] - c2.size[k]/2 for k in range(3)]
        max2 = [t2.position[k] + c2.size[k]/2 for k in range(3)]
        return all(min1[k] <= max2[k] and max1[k] >= min2[k] for k in range(3))

    def _resolve_collision(self, e1, e2):
        v1, v2 = e1.get_component(Velocity), e2.get_component(Velocity)
        if v1: v1.vector = [0.0, 0.0, 0.0]
        if v2: v2.vector = [0.0, 0.0, 0.0]

class SemanticPhysicsSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Collider, SemanticMaterial)
        for entity in entities:
            collider = entity.get_component(Collider)
            mat_self = entity.get_component(SemanticMaterial)
            for other_uid in collider.collisions:
                other = self.world.entity_manager.get_entity(other_uid)
                if other and other.has_component(SemanticMaterial):
                    self._resolve_semantic_interaction(entity, mat_self, other, other.get_component(SemanticMaterial))

    def _resolve_semantic_interaction(self, e1, m1, e2, m2):
        if m1.material == "fire" and "flammable" in m2.properties:
            if "burning" not in m2.properties:
                m2.properties.append("burning")
                self.world.kernel.dispatch("world:interaction", {
                    "type": "ignite", "subject": e1.uid, "subject_name": e1.get_component(Name).name,
                    "object": e2.uid, "object_name": e2.get_component(Name).name
                })
        if m1.material == "water" and (m2.material == "fire" or "burning" in m2.properties):
            if "burning" in m2.properties:
                m2.properties.remove("burning")
                self.world.kernel.dispatch("world:interaction", {
                    "type": "extinguish", "subject": e1.uid, "subject_name": e1.get_component(Name).name,
                    "object": e2.uid, "object_name": e2.get_component(Name).name
                })

class ScriptSystem(System):
    def update(self, delta_time: float):
        entities = self.world.entity_manager.get_entities_with(Script)
        for entity in entities:
            script = entity.get_component(Script)
            try:
                # SAFE EXECUTION SANDBOX
                # We strictly limit what the script can access.
                # It cannot import os, sys, or subprocess.
                safe_builtins = {
                    "print": print,
                    "range": range,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "abs": abs,
                    "max": max,
                    "min": min,
                    "round": round,
                    "__import__": self._safe_import
                }
                
                name = entity.get_component(Name).name if entity.get_component(Name) else "Unknown"
                collisions = entity.get_component(Collider).collisions if entity.has_component(Collider) else []
                velocity = entity.get_component(Velocity) # Allow direct velocity access
                
                local_scope = {
                    "entity": entity, 
                    "dt": delta_time, 
                    "state": script.state, 
                    "name": name, 
                    "collisions": collisions,
                    "Velocity": Velocity, # Expose component types
                    "Transform": Transform
                }
                
                exec(script.source_code, {"__builtins__": safe_builtins}, local_scope)
            except Exception as e:
                print(f"[ScriptSystem] Error in entity {entity.uid}: {e}")

    def _safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        # Whitelist imports
        if name in ["math", "random", "time", "json"]:
            return __import__(name, globals, locals, fromlist, level)
        raise ImportError(f"Import of '{name}' is forbidden by sandbox.")

class PhysicsSystem(System):
    def update(self, delta_time: float):
        pass
