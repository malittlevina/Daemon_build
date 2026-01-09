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

class Collider(Component):
    """Axis-Aligned Bounding Box (AABB) for collision."""
    def __init__(self, size=(1.0, 1.0, 1.0), is_trigger=False):
        self.size = list(size)
        self.is_trigger = is_trigger # If True, detects overlap but doesn't block movement
        self.collisions = [] # List of entity UIDs currently colliding with

class SpatialAnchor(Component):
    """
    Links this entity to a persistent real-world location.
    anchor_id: The UUID provided by the AR/Cloud Anchor service.
    offset: Relative transform from the anchor.
    """
    def __init__(self, anchor_id: str, offset_pos=(0,0,0)):
        self.anchor_id = anchor_id
        self.offset_pos = list(offset_pos)

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

class SemanticMaterial(Component):
    """
    Defines what an object 'is' conceptually for semantic physics.
    E.g., material="wood", properties=["flammable", "solid"]
    """
    def __init__(self, material: str, properties: List[str] = None):
        self.material = material
        self.properties = properties or []

    def __repr__(self):
        return f"Material({self.material}, {self.properties})"

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

class UIWindow(Component):
    """Represents a floating GUI window in 3D space."""
    def __init__(self, pid: str, width=1.0, height=0.7):
        self.pid = pid
        self.width = width
        self.height = height
