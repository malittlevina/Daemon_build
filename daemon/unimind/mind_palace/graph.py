from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


DEFAULT_ROOMS = {
    "geometry": {"shape_ops", "primitives", "constraints", "prefabs"},
    "math": {"arithmetic", "algebra", "geometry", "statistics"},
    "science": {"biology", "chemistry", "physics", "earth_science"},
    "history": {"ancient", "medieval", "modern", "civics"},
    "english": {"grammar", "writing", "literature", "vocabulary"},
    "materials": {"pbr", "textures", "shaders"},
    "physics": {"colliders", "rigid_bodies", "constraints"},
    "story": {"characters", "plot", "dialogue"},
    "world_rules": {"factions", "economy", "magic", "laws"},
}


def _infer_room(tags: Sequence[str]) -> str:
    t = set(tags or [])
    if any(x.startswith(("shape.", "geo.", "geometry", "cad")) for x in t) or "geometry" in t:
        return "geometry"
    if "math" in t or any(x.startswith(("math.", "algebra", "arithmetic", "geometry.")) for x in t):
        return "math"
    if "science" in t or any(x.startswith(("bio", "chem", "phys", "earth_science")) for x in t):
        return "science"
    if "history" in t or "civics" in t:
        return "history"
    if "english" in t or any(x.startswith(("grammar", "writing", "vocab", "literature")) for x in t):
        return "english"
    if any(x.startswith(("mat.", "material", "pbr", "shader")) for x in t) or "materials" in t:
        return "materials"
    if any(x.startswith(("phys.", "physics", "rigid", "collider")) for x in t) or "physics" in t:
        return "physics"
    if any(x.startswith(("story", "plot", "character")) for x in t):
        return "story"
    return "world_rules"


def _infer_shelf(room: str, tags: Sequence[str]) -> str:
    t = set(tags or [])
    if room == "geometry":
        if any(x in t for x in ("prefab", "prefabs")):
            return "prefabs"
        if any(x.startswith("shape.op") or x.startswith("shape.") for x in t):
            return "shape_ops"
        if any(x in t for x in ("primitive", "primitives")):
            return "primitives"
        return "constraints" if "constraint" in t else "shape_ops"
    if room == "math":
        if "algebra" in t:
            return "algebra"
        if "statistics" in t:
            return "statistics"
        if any(x in t for x in ("geometry", "geometry.math")):
            return "geometry"
        return "arithmetic"
    if room == "science":
        if "biology" in t:
            return "biology"
        if "chemistry" in t:
            return "chemistry"
        if "physics" in t:
            return "physics"
        return "earth_science"
    if room == "history":
        if "civics" in t:
            return "civics"
        if "ancient" in t:
            return "ancient"
        if "medieval" in t:
            return "medieval"
        return "modern"
    if room == "english":
        if "grammar" in t:
            return "grammar"
        if "writing" in t:
            return "writing"
        if "vocabulary" in t:
            return "vocabulary"
        return "literature"
    # default shelf when unknown
    return next(iter(DEFAULT_ROOMS.get(room, {"misc"})))


@dataclass
class MindPalace:
    """
    A small semantic graph:
    - Rooms/shelves for coarse routing
    - Nodes are artifact IDs
    - Edges encode relationships ("related", "requires", "example_of", etc.)
    """

    rooms: Dict[str, Dict[str, Set[str]]] = field(default_factory=dict)
    edges: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.rooms:
            self.rooms = {r: {s: set() for s in shelves} for r, shelves in DEFAULT_ROOMS.items()}

    def place(self, artifact_id: str, *, tags: Sequence[str] = ()) -> Dict[str, str]:
        room = _infer_room(tags)
        shelf = _infer_shelf(room, tags)
        self.rooms.setdefault(room, {}).setdefault(shelf, set()).add(artifact_id)
        return {"room": room, "shelf": shelf}

    def link(self, src: str, dst: str, *, kind: str = "related", weight: float = 0.5, meta: Optional[Dict[str, Any]] = None) -> None:
        self.edges.append({"from": src, "to": dst, "type": kind, "weight": weight, "meta": meta or {}})

    def list_room(self, room: str) -> Dict[str, List[str]]:
        shelves = self.rooms.get(room, {})
        return {s: sorted(list(ids)) for s, ids in shelves.items()}

    def retrieve(
        self,
        *,
        room: Optional[str] = None,
        shelves: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        limit: int = 10,
    ) -> List[str]:
        # MindPalace retrieval is purely by placement; semantic ranking happens in KnowledgeStore.
        tags = list(tags or [])
        rooms = [room] if room else list(self.rooms.keys())
        out: List[str] = []
        for r in rooms:
            shelf_map = self.rooms.get(r, {})
            shelf_names = list(shelves) if shelves else list(shelf_map.keys())
            for s in shelf_names:
                for aid in sorted(list(shelf_map.get(s, set()))):
                    out.append(aid)
                    if len(out) >= limit:
                        return out
        return out

