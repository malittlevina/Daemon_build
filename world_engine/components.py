from world_engine.ecs import Component
from typing import List, Tuple

# --- Spatial Components ---

class Transform(Component):
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
        self.position = list(position)
        self.rotation = list(rotation)
        self.scale = list(scale)

    def __repr__(self):
        return f"Transform(pos={self.position}, rot={self.rotation})"

class Velocity(Component):
    def __init__(self, vector=(0.0, 0.0, 0.0)):
        self.vector = list(vector)

# --- Identity & Logic ---

class Name(Component):
    def __init__(self, name: str):
        self.name = name

class Tag(Component):
    def __init__(self, tags: List[str]):
        self.tags = set(tags)

class Script(Component):
    """Allows attaching arbitrary python code/behavior to an entity."""
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.state = {}

# --- Rendering / Representation (Symbolic) ---

class Mesh(Component):
    """Symbolic representation of 3D geometry."""
    def __init__(self, asset_id: str, material_id: str = "default"):
        self.asset_id = asset_id
        self.material_id = material_id

class Light(Component):
    def __init__(self, color=(1.0, 1.0, 1.0), intensity=1.0, type="point"):
        self.color = color
        self.intensity = intensity
        self.type = type
