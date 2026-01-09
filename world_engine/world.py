from core.module import Module
from world_engine.ecs import EntityManager
from world_engine.systems import MovementSystem, ScriptSystem, PhysicsSystem
from world_engine.components import Transform, Name
import time
import threading

class WorldEngine(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.entity_manager = EntityManager()
        self.systems = []
        self.running = False
        self.thread = None
        self.target_fps = 60
        self.tick_rate = 1.0 / self.target_fps

    def initialize(self):
        # Register default systems
        self.add_system(MovementSystem(self))
        self.add_system(PhysicsSystem(self))
        self.add_system(ScriptSystem(self))
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
