from core.module import Module
import os

class Holodeck(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.file_entities = {} # path -> entity_uid

    def initialize(self):
        self.kernel.log("Holodeck", "Spatial File System Visualizer Initialized.")
        self.kernel.events.subscribe("file:created", self.on_file_created)
        self.kernel.events.subscribe("file:deleted", self.on_file_deleted)

    def start(self):
        pass

    def stop(self):
        pass

    def on_file_created(self, event_type, data):
        path = data.get("path")
        if not path: return

        world = self.kernel.get_module("world")
        if not world: return

        # Determine semantics based on extension
        ext = os.path.splitext(path)[1]
        material = "paper"
        if ext == ".py": material = "script"
        elif ext == ".db": material = "metal"
        elif ext == ".json": material = "glass"

        # Create physical representation
        uid = world.create_object(f"File: {os.path.basename(path)}", position=(0, 5, 0)) # Drop from sky
        world.add_physics(uid, collider_size=(0.5, 0.5, 0.5))
        world.add_semantic_material(uid, material, properties=["flammable"] if material == "paper" else [])
        
        self.file_entities[path] = uid
        self.kernel.log("Holodeck", f"Materialized file {path} as entity {uid} ({material})")

    def on_file_deleted(self, event_type, data):
        path = data.get("path")
        if path in self.file_entities:
            uid = self.file_entities[path]
            world = self.kernel.get_module("world")
            if world:
                # In a real engine, we might play a 'disintegrate' effect first
                world.entity_manager.destroy_entity(uid)
                self.kernel.log("Holodeck", f"Dematerialized file {path}")
            del self.file_entities[path]
