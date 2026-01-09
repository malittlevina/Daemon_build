from core.module import Module
from world_engine.ecs import EntityManager
from world_engine.systems import MovementSystem, ScriptSystem, PhysicsSystem, CollisionSystem, SemanticPhysicsSystem
from world_engine.hud import HUDSystem
from world_engine.components import Transform, Name, Velocity, Collider, Script, SemanticMaterial, UIWindow, Mesh
from world_engine.serializer import WorldSerializer
import time
import threading
import os

class WorldEngine(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.entity_manager = EntityManager()
        self.systems = []
        self.running = False
        self.thread = None
        self.target_fps = 60
        self.tick_rate = 1.0 / self.target_fps
        self.serializer = WorldSerializer()

    def initialize(self):
        # Register default systems
        self.add_system(MovementSystem(self))
        self.add_system(CollisionSystem(self))
        self.add_system(SemanticPhysicsSystem(self))
        self.add_system(PhysicsSystem(self))
        self.add_system(ScriptSystem(self))
        self.add_system(HUDSystem(self))
        self.kernel.log("WorldEngine", "Initialized.")

    def add_system(self, system):
        self.systems.append(system)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._game_loop, daemon=True)
        self.thread.start()
        self.kernel.log("WorldEngine", "Simulation loop started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.kernel.log("WorldEngine", "Simulation stopped.")

    def _game_loop(self):
        last_time = time.time()
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            # Update all systems
            for system in self.systems:
                try:
                    system.update(delta_time)
                except Exception as e:
                    self.kernel.log("WorldEngine", f"System Error: {e}", level="error")

            # Sleep to maintain tick rate
            elapsed = time.time() - current_time
            sleep_time = max(0, self.tick_rate - elapsed)
            time.sleep(sleep_time)

    # --- Public API for Daemon ---

    def create_object(self, name: str, position=(0,0,0)):
        """Create a basic game object with a Transform."""
        entity = self.entity_manager.create_entity()
        entity.add_component(Name(name))
        entity.add_component(Transform(position))
        self.kernel.log("WorldEngine", f"Created object '{name}' at {position} (ID: {entity.uid})")
        return entity.uid

    def create_hud_window(self, title, content):
        """Public API to spawn a floating UI window."""
        uid = self.create_object(f"HUD: {title}", position=(0, 1.5, 2))
        entity = self.entity_manager.get_entity(uid)
        entity.add_component(UIWindow(pid="sys", width=0.8, height=0.5))
        entity.add_component(Mesh(asset_id="plane_16:9", material_id="glass_ui"))
        self.kernel.log("WorldEngine", f"Spawned HUD Window: {title}")
        return uid

    def add_physics(self, uid, velocity=(0,0,0), collider_size=(1,1,1), trigger=False):
        entity = self.entity_manager.get_entity(uid)
        if entity:
            entity.add_component(Velocity(velocity))
            entity.add_component(Collider(collider_size, is_trigger=trigger))
            return True
        return False

    def add_semantic_material(self, uid, material, properties=None):
        entity = self.entity_manager.get_entity(uid)
        if entity:
            entity.add_component(SemanticMaterial(material, properties))
            return True
        return False

    def add_script(self, uid, code):
        entity = self.entity_manager.get_entity(uid)
        if entity:
            entity.add_component(Script(code))
            return True
        return False

    def get_object_info(self, uid):
        entity = self.entity_manager.get_entity(uid)
        if not entity:
            return None
        
        info = {"uid": uid, "components": {}}
        for comp_type, comp in entity.components.items():
            info["components"][comp_type.__name__] = vars(comp)
        return info

    def list_objects(self):
        entities = self.entity_manager.entities.values()
        return [f"{e.uid}: {e.get_component(Name).name if e.get_component(Name) else 'Unnamed'}" for e in entities]

    def save_world(self, filename="world.json"):
        path = os.path.join("worlds", filename)
        os.makedirs("worlds", exist_ok=True)
        try:
            data = self.serializer.serialize(self.entity_manager)
            with open(path, "w") as f:
                f.write(data)
            self.kernel.log("WorldEngine", f"Saved world to {path}")
            return f"Saved to {path}"
        except Exception as e:
            self.kernel.log("WorldEngine", f"Save failed: {e}", level="error")
            return f"Error: {e}"

    def load_world(self, filename="world.json"):
        path = os.path.join("worlds", filename)
        try:
            with open(path, "r") as f:
                data = f.read()
            self.entity_manager = self.serializer.deserialize(data)
            self.kernel.log("WorldEngine", f"Loaded world from {path}")
            return f"Loaded {len(self.entity_manager.entities)} entities."
        except Exception as e:
            self.kernel.log("WorldEngine", f"Load failed: {e}", level="error")
            return f"Error: {e}"
