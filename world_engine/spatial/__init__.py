# world_engine/spatial/__init__.py
"""
Spatial systems for the World Engine.

Provides:
- Spatial indexing (grid, octree)
- Collision detection broad phase
- Spatial queries (raycast, box, sphere)
- Zones and regions
"""

from world_engine.spatial.spatial_index import SpatialIndex, SpatialCell
from world_engine.spatial.zone import Zone

__all__ = [
    "SpatialIndex",
    "SpatialCell",
    "Zone"
]
