# world_engine/entities/entity.py
"""
Entity - Base class for all world objects.

An entity is anything that exists in the world:
- Physical objects
- Triggers and zones
- Particles
- Agents/NPCs
- Abstract concepts
"""

import math
from typing import Dict, Any, Optional, List, Set, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid

if TYPE_CHECKING:
    from world_engine.world_core import WorldEngine


class EntityState(Enum):
    """Entity lifecycle states."""
    CREATED = auto()
    ACTIVE = auto()
    INACTIVE = auto()
    DESTROYING = auto()
    DESTROYED = auto()


@dataclass
class Transform:
    """
    Spatial transform for an entity.
    
    Represents position, rotation, and scale in 3D space.
    """
    
    position: tuple = (0.0, 0.0, 0.0)
    rotation: tuple = (0.0, 0.0, 0.0, 1.0)  # Quaternion (x, y, z, w)
    scale: tuple = (1.0, 1.0, 1.0)
    
    # Parent transform for hierarchies
    parent: Optional['Transform'] = None
    
    def set_position(self, x: float, y: float, z: float):
        """Set position."""
        self.position = (x, y, z)
    
    def translate(self, dx: float, dy: float, dz: float):
        """Move by offset."""
        self.position = (
            self.position[0] + dx,
            self.position[1] + dy,
            self.position[2] + dz
        )
    
    def set_rotation_euler(self, pitch: float, yaw: float, roll: float):
        """Set rotation from Euler angles (radians)."""
        # Convert Euler to quaternion
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        
        self.rotation = (
            sr * cp * cy - cr * sp * sy,  # x
            cr * sp * cy + sr * cp * sy,  # y
            cr * cp * sy - sr * sp * cy,  # z
            cr * cp * cy + sr * sp * sy   # w
        )
    
    def get_euler(self) -> tuple:
        """Get rotation as Euler angles (pitch, yaw, roll)."""
        x, y, z, w = self.rotation
        
        # Roll
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)
        
        # Yaw
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return (pitch, yaw, roll)
    
    def get_forward(self) -> tuple:
        """Get forward direction vector."""
        x, y, z, w = self.rotation
        return (
            2 * (x * z + w * y),
            2 * (y * z - w * x),
            1 - 2 * (x * x + y * y)
        )
    
    def get_right(self) -> tuple:
        """Get right direction vector."""
        x, y, z, w = self.rotation
        return (
            1 - 2 * (y * y + z * z),
            2 * (x * y + w * z),
            2 * (x * z - w * y)
        )
    
    def get_up(self) -> tuple:
        """Get up direction vector."""
        x, y, z, w = self.rotation
        return (
            2 * (x * y - w * z),
            1 - 2 * (x * x + z * z),
            2 * (y * z + w * x)
        )
    
    def get_world_position(self) -> tuple:
        """Get world position (considering parent hierarchy)."""
        if self.parent:
            parent_pos = self.parent.get_world_position()
            return (
                parent_pos[0] + self.position[0],
                parent_pos[1] + self.position[1],
                parent_pos[2] + self.position[2]
            )
        return self.position
    
    def distance_to(self, other: 'Transform') -> float:
        """Calculate distance to another transform."""
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        dz = other.position[2] - self.position[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def look_at(self, target: tuple):
        """Orient to look at a target position."""
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        dz = target[2] - self.position[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 0.0001:
            return
        
        yaw = math.atan2(dx, dz)
        pitch = -math.asin(dy / dist)
        
        self.set_rotation_euler(pitch, yaw, 0)


@dataclass
class Entity:
    """
    Base class for all world entities.
    
    An entity has:
    - Unique identity
    - Spatial transform
    - Tags for categorization
    - Custom properties
    - Optional components
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "entity"
    
    # Transform
    transform: Transform = field(default_factory=Transform)
    
    # State
    state: EntityState = EntityState.CREATED
    
    # Classification
    tags: Set[str] = field(default_factory=set)
    layer: int = 0  # Collision/render layer
    
    # Custom properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Components (optional additions like physics, rendering, etc.)
    components: Dict[str, Any] = field(default_factory=dict)
    
    # Parent/child relationships
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    # Reference to world
    world: Optional['WorldEngine'] = field(default=None, repr=False)
    
    # Lifecycle hooks
    _on_added: List[Callable] = field(default_factory=list)
    _on_removed: List[Callable] = field(default_factory=list)
    _on_tick: List[Callable] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization setup."""
        self.state = EntityState.ACTIVE
    
    # =========================================================================
    # Tags
    # =========================================================================
    
    def add_tag(self, tag: str):
        """Add a tag to the entity."""
        self.tags.add(tag)
        if self.world:
            if tag not in self.world._entities_by_tag:
                self.world._entities_by_tag[tag] = set()
            self.world._entities_by_tag[tag].add(self.id)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the entity."""
        self.tags.discard(tag)
        if self.world and tag in self.world._entities_by_tag:
            self.world._entities_by_tag[tag].discard(self.id)
    
    def has_tag(self, tag: str) -> bool:
        """Check if entity has a tag."""
        return tag in self.tags
    
    def has_any_tag(self, tags: List[str]) -> bool:
        """Check if entity has any of the given tags."""
        return any(tag in self.tags for tag in tags)
    
    def has_all_tags(self, tags: List[str]) -> bool:
        """Check if entity has all of the given tags."""
        return all(tag in self.tags for tag in tags)
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    def set_property(self, key: str, value: Any):
        """Set a custom property."""
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a custom property."""
        return self.properties.get(key, default)
    
    def has_property(self, key: str) -> bool:
        """Check if a property exists."""
        return key in self.properties
    
    # =========================================================================
    # Components
    # =========================================================================
    
    def add_component(self, name: str, component: Any):
        """Add a component to the entity."""
        self.components[name] = component
        if hasattr(component, 'entity'):
            component.entity = self
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name."""
        return self.components.get(name)
    
    def has_component(self, name: str) -> bool:
        """Check if entity has a component."""
        return name in self.components
    
    def remove_component(self, name: str) -> bool:
        """Remove a component."""
        if name in self.components:
            del self.components[name]
            return True
        return False
    
    # =========================================================================
    # Hierarchy
    # =========================================================================
    
    def set_parent(self, parent: 'Entity'):
        """Set parent entity."""
        if self.parent_id and self.world:
            old_parent = self.world.get_entity(self.parent_id)
            if old_parent:
                old_parent.children_ids.remove(self.id)
        
        self.parent_id = parent.id
        parent.children_ids.append(self.id)
        self.transform.parent = parent.transform
    
    def get_parent(self) -> Optional['Entity']:
        """Get parent entity."""
        if self.parent_id and self.world:
            return self.world.get_entity(self.parent_id)
        return None
    
    def get_children(self) -> List['Entity']:
        """Get child entities."""
        if not self.world:
            return []
        return [
            self.world.get_entity(cid)
            for cid in self.children_ids
            if self.world.get_entity(cid)
        ]
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def on_added_to_world(self):
        """Called when entity is added to world."""
        for hook in self._on_added:
            hook(self)
    
    def on_removed_from_world(self):
        """Called when entity is removed from world."""
        for hook in self._on_removed:
            hook(self)
    
    def tick(self, dt: float):
        """Called each simulation tick."""
        for hook in self._on_tick:
            hook(self, dt)
    
    def destroy(self):
        """Mark entity for destruction."""
        self.state = EntityState.DESTROYING
        if self.world:
            self.world.remove_entity(self.id)
    
    # =========================================================================
    # Spatial
    # =========================================================================
    
    @property
    def position(self) -> tuple:
        """Get position."""
        return self.transform.position
    
    @position.setter
    def position(self, value: tuple):
        """Set position."""
        self.transform.position = value
        if self.world:
            self.world.spatial.update(self)
    
    def distance_to(self, other: 'Entity') -> float:
        """Calculate distance to another entity."""
        return self.transform.distance_to(other.transform)
    
    def get_nearby(self, radius: float) -> List['Entity']:
        """Get entities within radius."""
        if self.world:
            return self.world.query_sphere(self.position, radius)
        return []
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "position": self.transform.position,
            "rotation": self.transform.rotation,
            "scale": self.transform.scale,
            "tags": list(self.tags),
            "layer": self.layer,
            "properties": self.properties,
            "parent_id": self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Deserialize entity from dictionary."""
        entity = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "entity")
        )
        entity.transform.position = tuple(data.get("position", (0, 0, 0)))
        entity.transform.rotation = tuple(data.get("rotation", (0, 0, 0, 1)))
        entity.transform.scale = tuple(data.get("scale", (1, 1, 1)))
        entity.tags = set(data.get("tags", []))
        entity.layer = data.get("layer", 0)
        entity.properties = data.get("properties", {})
        entity.parent_id = data.get("parent_id")
        return entity
