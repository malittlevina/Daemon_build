from core.module import Module
import random
import math

class Architect(Module):
    def __init__(self, kernel):
        super().__init__(kernel)

    def initialize(self):
        self.kernel.log("Architect", "Initialized. Ready to build.")

    def start(self):
        pass

    def stop(self):
        pass

    def generate_terrain(self, width=10, depth=10, roughness=0.5):
        """Generates a procedural terrain using simple noise."""
        world = self.kernel.get_module("world")
        if not world: return "World Engine not found."

        self.kernel.log("Architect", f"Generating terrain {width}x{depth}...")
        
        count = 0
        for x in range(width):
            for z in range(depth):
                # Simple Perlin-ish noise approximation
                # Height based on sin waves for now
                height = math.sin(x * roughness) + math.cos(z * roughness)
                height = int(height * 2) # Quantize
                
                uid = world.create_object(f"Ground_{x}_{z}", position=(x, height, z))
                world.add_physics(uid, collider_size=(1, 1, 1))
                world.add_semantic_material(uid, "stone")
                count += 1
        
        return f"Generated {count} terrain blocks."

    def generate_room(self, x, y, z, w, h, material="wood"):
        """Generates a hollow room."""
        world = self.kernel.get_module("world")
        if not world: return
        
        count = 0
        for dx in range(w):
            for dy in range(h):
                for dz in range(w):
                    # Only walls, floor, ceiling
                    if dx == 0 or dx == w-1 or dy == 0 or dy == h-1 or dz == 0 or dz == w-1:
                        uid = world.create_object(f"Wall_{x+dx}_{y+dy}_{z+dz}", (x+dx, y+dy, z+dz))
                        world.add_physics(uid, collider_size=(1,1,1))
                        world.add_semantic_material(uid, material)
                        count += 1
        return f"Built room with {count} blocks."
