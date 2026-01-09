# world_engine/spatial/spatial_index.py
"""
Spatial Index - Spatial partitioning for efficient queries.

Provides:
- Grid-based spatial hashing
- Broad phase collision detection
- Spatial queries (sphere, box, ray)
"""

import math
from typing import Dict, Any, Optional, List, Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from world_engine.world_core import WorldEngine
    from world_engine.entities.entity import Entity


@dataclass
class SpatialCell:
    """A cell in the spatial grid."""
    x: int
    y: int
    z: int
    entities: Set[str] = field(default_factory=set)
    
    @property
    def key(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)


class SpatialIndex:
    """
    Spatial hash grid for efficient spatial queries.
    
    Divides the world into cells and tracks which entities
    are in each cell for fast neighbor queries.
    """
    
    def __init__(self, world: 'WorldEngine', cell_size: float = 10.0):
        """Initialize the spatial index."""
        self.world = world
        self.cell_size = cell_size
        self.inverse_cell_size = 1.0 / cell_size
        
        # Grid cells
        self._cells: Dict[Tuple[int, int, int], SpatialCell] = {}
        
        # Entity -> cell mapping
        self._entity_cells: Dict[str, Set[Tuple[int, int, int]]] = {}
        
        print(f"[SpatialIndex] Initialized with cell size {cell_size}")
    
    def _position_to_cell(self, position: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Convert world position to cell coordinates."""
        return (
            int(math.floor(position[0] * self.inverse_cell_size)),
            int(math.floor(position[1] * self.inverse_cell_size)),
            int(math.floor(position[2] * self.inverse_cell_size))
        )
    
    def _get_cell(self, key: Tuple[int, int, int]) -> SpatialCell:
        """Get or create a cell."""
        if key not in self._cells:
            self._cells[key] = SpatialCell(key[0], key[1], key[2])
        return self._cells[key]
    
    def _get_entity_radius(self, entity: 'Entity') -> float:
        """Get the radius of an entity for spatial purposes."""
        if entity.has_component("physics"):
            body = entity.get_component("physics")
            return body.get_bounding_sphere_radius()
        return 0.5  # Default radius
    
    def _get_covered_cells(self, position: Tuple[float, float, float], radius: float) -> List[Tuple[int, int, int]]:
        """Get all cells that an entity's bounding sphere overlaps."""
        cells = []
        
        min_cell = self._position_to_cell((
            position[0] - radius,
            position[1] - radius,
            position[2] - radius
        ))
        max_cell = self._position_to_cell((
            position[0] + radius,
            position[1] + radius,
            position[2] + radius
        ))
        
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    cells.append((x, y, z))
        
        return cells
    
    # =========================================================================
    # Entity management
    # =========================================================================
    
    def insert(self, entity: 'Entity'):
        """Insert an entity into the spatial index."""
        position = entity.transform.position
        radius = self._get_entity_radius(entity)
        
        cells = self._get_covered_cells(position, radius)
        self._entity_cells[entity.id] = set(cells)
        
        for cell_key in cells:
            cell = self._get_cell(cell_key)
            cell.entities.add(entity.id)
    
    def remove(self, entity: 'Entity'):
        """Remove an entity from the spatial index."""
        if entity.id not in self._entity_cells:
            return
        
        cells = self._entity_cells[entity.id]
        
        for cell_key in cells:
            if cell_key in self._cells:
                self._cells[cell_key].entities.discard(entity.id)
                # Clean up empty cells
                if not self._cells[cell_key].entities:
                    del self._cells[cell_key]
        
        del self._entity_cells[entity.id]
    
    def update(self, entity: 'Entity'):
        """Update an entity's position in the index."""
        self.remove(entity)
        self.insert(entity)
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def query_sphere(self, center: Tuple[float, float, float], radius: float) -> List['Entity']:
        """Query all entities within a sphere."""
        results = []
        checked = set()
        
        # Get cells that overlap the query sphere
        cells = self._get_covered_cells(center, radius)
        
        for cell_key in cells:
            if cell_key not in self._cells:
                continue
            
            for entity_id in self._cells[cell_key].entities:
                if entity_id in checked:
                    continue
                checked.add(entity_id)
                
                entity = self.world.get_entity(entity_id)
                if not entity:
                    continue
                
                # Distance check
                pos = entity.transform.position
                dx = pos[0] - center[0]
                dy = pos[1] - center[1]
                dz = pos[2] - center[2]
                dist_sq = dx*dx + dy*dy + dz*dz
                
                entity_radius = self._get_entity_radius(entity)
                max_dist = radius + entity_radius
                
                if dist_sq <= max_dist * max_dist:
                    results.append(entity)
        
        return results
    
    def query_box(
        self,
        min_point: Tuple[float, float, float],
        max_point: Tuple[float, float, float]
    ) -> List['Entity']:
        """Query all entities within an axis-aligned box."""
        results = []
        checked = set()
        
        min_cell = self._position_to_cell(min_point)
        max_cell = self._position_to_cell(max_point)
        
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    cell_key = (x, y, z)
                    if cell_key not in self._cells:
                        continue
                    
                    for entity_id in self._cells[cell_key].entities:
                        if entity_id in checked:
                            continue
                        checked.add(entity_id)
                        
                        entity = self.world.get_entity(entity_id)
                        if not entity:
                            continue
                        
                        pos = entity.transform.position
                        radius = self._get_entity_radius(entity)
                        
                        # AABB intersection
                        if (pos[0] + radius >= min_point[0] and
                            pos[0] - radius <= max_point[0] and
                            pos[1] + radius >= min_point[1] and
                            pos[1] - radius <= max_point[1] and
                            pos[2] + radius >= min_point[2] and
                            pos[2] - radius <= max_point[2]):
                            results.append(entity)
        
        return results
    
    def query_point(self, point: Tuple[float, float, float]) -> List['Entity']:
        """Query all entities containing a point."""
        results = []
        cell_key = self._position_to_cell(point)
        
        if cell_key not in self._cells:
            return results
        
        for entity_id in self._cells[cell_key].entities:
            entity = self.world.get_entity(entity_id)
            if not entity:
                continue
            
            pos = entity.transform.position
            radius = self._get_entity_radius(entity)
            
            dx = point[0] - pos[0]
            dy = point[1] - pos[1]
            dz = point[2] - pos[2]
            dist_sq = dx*dx + dy*dy + dz*dz
            
            if dist_sq <= radius * radius:
                results.append(entity)
        
        return results
    
    def raycast(
        self,
        origin: Tuple[float, float, float],
        direction: Tuple[float, float, float],
        max_distance: float = 1000.0
    ) -> List[Tuple['Entity', float]]:
        """
        Cast a ray and return hit entities with distances.
        
        Returns list of (entity, distance) tuples, sorted by distance.
        """
        results = []
        checked = set()
        
        # Normalize direction
        length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
        if length < 0.0001:
            return results
        
        dx, dy, dz = direction[0]/length, direction[1]/length, direction[2]/length
        
        # March along ray
        step_size = self.cell_size * 0.5
        t = 0.0
        
        while t < max_distance:
            point = (
                origin[0] + dx * t,
                origin[1] + dy * t,
                origin[2] + dz * t
            )
            
            cell_key = self._position_to_cell(point)
            
            if cell_key in self._cells:
                for entity_id in self._cells[cell_key].entities:
                    if entity_id in checked:
                        continue
                    checked.add(entity_id)
                    
                    entity = self.world.get_entity(entity_id)
                    if not entity:
                        continue
                    
                    # Ray-sphere intersection
                    pos = entity.transform.position
                    radius = self._get_entity_radius(entity)
                    
                    hit_dist = self._ray_sphere_intersection(
                        origin, (dx, dy, dz), pos, radius
                    )
                    
                    if hit_dist is not None and hit_dist <= max_distance:
                        results.append((entity, hit_dist))
            
            t += step_size
        
        # Sort by distance
        results.sort(key=lambda x: x[1])
        return results
    
    def _ray_sphere_intersection(
        self,
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        sphere_center: Tuple[float, float, float],
        sphere_radius: float
    ) -> Optional[float]:
        """Calculate ray-sphere intersection distance."""
        # Vector from ray origin to sphere center
        oc = (
            ray_origin[0] - sphere_center[0],
            ray_origin[1] - sphere_center[1],
            ray_origin[2] - sphere_center[2]
        )
        
        a = ray_dir[0]**2 + ray_dir[1]**2 + ray_dir[2]**2
        b = 2.0 * (oc[0]*ray_dir[0] + oc[1]*ray_dir[1] + oc[2]*ray_dir[2])
        c = oc[0]**2 + oc[1]**2 + oc[2]**2 - sphere_radius**2
        
        discriminant = b*b - 4*a*c
        
        if discriminant < 0:
            return None
        
        t = (-b - math.sqrt(discriminant)) / (2*a)
        
        if t < 0:
            t = (-b + math.sqrt(discriminant)) / (2*a)
        
        return t if t >= 0 else None
    
    # =========================================================================
    # Collision detection (broad phase)
    # =========================================================================
    
    def get_collision_pairs(self) -> List[Tuple[str, str]]:
        """Get all potential collision pairs."""
        pairs = set()
        
        for cell in self._cells.values():
            entities = list(cell.entities)
            
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    # Ensure consistent ordering
                    pair = tuple(sorted([entities[i], entities[j]]))
                    pairs.add(pair)
        
        return list(pairs)
    
    def get_nearby_entities(self, entity: 'Entity', radius: float = None) -> List['Entity']:
        """Get entities near a given entity."""
        if radius is None:
            radius = self._get_entity_radius(entity) * 2
        
        results = self.query_sphere(entity.transform.position, radius)
        
        # Remove the querying entity itself
        return [e for e in results if e.id != entity.id]
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get spatial index statistics."""
        total_entities = sum(len(cell.entities) for cell in self._cells.values())
        
        return {
            "cell_count": len(self._cells),
            "tracked_entities": len(self._entity_cells),
            "cell_size": self.cell_size,
            "avg_entities_per_cell": total_entities / max(1, len(self._cells))
        }
    
    def clear(self):
        """Clear the spatial index."""
        self._cells.clear()
        self._entity_cells.clear()
