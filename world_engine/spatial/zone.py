# world_engine/spatial/zone.py
"""
Zone - Spatial regions with special properties.

Zones are areas of the world with:
- Custom physics properties
- Trigger behaviors
- Narrative significance
"""

from typing import Dict, Any, Optional, List, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


class ZoneShape(Enum):
    """Zone shapes."""
    BOX = auto()
    SPHERE = auto()
    CYLINDER = auto()
    POLYGON = auto()  # 2D polygon extruded in Y


@dataclass
class Zone:
    """
    A spatial zone with special properties.
    
    Zones can:
    - Modify physics (different gravity, no gravity, water)
    - Trigger events when entities enter/exit
    - Have narrative significance
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "zone"
    
    # Shape
    shape: ZoneShape = ZoneShape.BOX
    
    # Bounds (for box: (min, max), for sphere: center + radius)
    bounds: tuple = ((-10, -10, -10), (10, 10, 10))
    center: Tuple[float, float, float] = (0, 0, 0)
    radius: float = 10.0
    height: float = 20.0  # For cylinder
    
    # Physics overrides
    override_gravity: bool = False
    gravity: Tuple[float, float, float] = (0, -9.81, 0)
    
    drag_multiplier: float = 1.0  # Water would be high
    friction_multiplier: float = 1.0  # Ice would be low
    
    # Zone type tags
    tags: Set[str] = field(default_factory=set)
    
    # Properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    _entities_inside: Set[str] = field(default_factory=set)
    
    # Callbacks
    _on_enter: List[Callable] = field(default_factory=list)
    _on_exit: List[Callable] = field(default_factory=list)
    _on_stay: List[Callable] = field(default_factory=list)
    
    # State
    enabled: bool = True
    
    def contains(self, position: Tuple[float, float, float]) -> bool:
        """Check if a position is inside the zone."""
        if not self.enabled:
            return False
        
        if self.shape == ZoneShape.BOX:
            min_pt, max_pt = self.bounds
            return (
                min_pt[0] <= position[0] <= max_pt[0] and
                min_pt[1] <= position[1] <= max_pt[1] and
                min_pt[2] <= position[2] <= max_pt[2]
            )
        
        elif self.shape == ZoneShape.SPHERE:
            dx = position[0] - self.center[0]
            dy = position[1] - self.center[1]
            dz = position[2] - self.center[2]
            return (dx*dx + dy*dy + dz*dz) <= self.radius * self.radius
        
        elif self.shape == ZoneShape.CYLINDER:
            # Check horizontal distance
            dx = position[0] - self.center[0]
            dz = position[2] - self.center[2]
            if (dx*dx + dz*dz) > self.radius * self.radius:
                return False
            
            # Check vertical
            half_height = self.height / 2
            return abs(position[1] - self.center[1]) <= half_height
        
        return False
    
    def update_entity(self, entity_id: str, position: Tuple[float, float, float]) -> Optional[str]:
        """
        Update an entity's status in the zone.
        
        Returns: 'enter', 'exit', 'stay', or None
        """
        is_inside = self.contains(position)
        was_inside = entity_id in self._entities_inside
        
        if is_inside and not was_inside:
            self._entities_inside.add(entity_id)
            for callback in self._on_enter:
                callback(entity_id, self)
            return 'enter'
        
        elif not is_inside and was_inside:
            self._entities_inside.discard(entity_id)
            for callback in self._on_exit:
                callback(entity_id, self)
            return 'exit'
        
        elif is_inside and was_inside:
            for callback in self._on_stay:
                callback(entity_id, self)
            return 'stay'
        
        return None
    
    def on_enter(self, callback: Callable[[str, 'Zone'], None]):
        """Register enter callback."""
        self._on_enter.append(callback)
    
    def on_exit(self, callback: Callable[[str, 'Zone'], None]):
        """Register exit callback."""
        self._on_exit.append(callback)
    
    def on_stay(self, callback: Callable[[str, 'Zone'], None]):
        """Register stay callback."""
        self._on_stay.append(callback)
    
    def get_entities_inside(self) -> Set[str]:
        """Get IDs of entities currently inside."""
        return set(self._entities_inside)


# Predefined zone types

class WaterZone(Zone):
    """A water zone with swimming physics."""
    
    def __init__(self, center: Tuple[float, float, float], size: Tuple[float, float, float]):
        half = (size[0]/2, size[1]/2, size[2]/2)
        super().__init__(
            name="water",
            shape=ZoneShape.BOX,
            bounds=(
                (center[0]-half[0], center[1]-half[1], center[2]-half[2]),
                (center[0]+half[0], center[1]+half[1], center[2]+half[2])
            ),
            override_gravity=True,
            gravity=(0, -2.0, 0),  # Reduced gravity
            drag_multiplier=5.0,
            tags={"water", "liquid", "swimmable"}
        )


class NoGravityZone(Zone):
    """A zero-gravity zone."""
    
    def __init__(self, center: Tuple[float, float, float], radius: float):
        super().__init__(
            name="zero_g",
            shape=ZoneShape.SPHERE,
            center=center,
            radius=radius,
            override_gravity=True,
            gravity=(0, 0, 0),
            tags={"zero_gravity", "space"}
        )


class TriggerZone(Zone):
    """A trigger zone for events."""
    
    def __init__(
        self,
        name: str,
        center: Tuple[float, float, float],
        size: Tuple[float, float, float],
        event_name: str
    ):
        half = (size[0]/2, size[1]/2, size[2]/2)
        super().__init__(
            name=name,
            shape=ZoneShape.BOX,
            bounds=(
                (center[0]-half[0], center[1]-half[1], center[2]-half[2]),
                (center[0]+half[0], center[1]+half[1], center[2]+half[2])
            ),
            tags={"trigger"}
        )
        self.event_name = event_name
