# observer/mind_palace.py
"""
Mind Palace (Method of Loci)
============================
A spatial organization system for memories, inspired by the ancient
memory technique. Memories are placed in rooms and locations within
an imagined architectural space.

The daemon can walk through its palace to retrieve memories,
each room containing related memories that can be visualized
and accessed through spatial navigation.
"""

import os
import json
import time
import uuid
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple

from .moment import Moment, MomentType, Significance


class RoomType(Enum):
    """Types of rooms in the mind palace."""
    # Core rooms
    ENTRANCE_HALL = "entrance_hall"       # Recent memories, arrivals
    LIBRARY = "library"                    # Knowledge, facts, learnings
    GALLERY = "gallery"                    # Visual memories, images
    MUSIC_ROOM = "music_room"              # Audio memories, sounds
    STUDY = "study"                        # Deep work, concentration
    
    # Personal rooms
    BEDROOM = "bedroom"                    # Personal, intimate memories
    LIVING_ROOM = "living_room"            # Daily life, routines
    KITCHEN = "kitchen"                    # Nourishment, comfort
    GARDEN = "garden"                      # Growth, nature, peace
    
    # Special rooms
    VAULT = "vault"                        # Protected, important memories
    OBSERVATORY = "observatory"            # Big picture, insights
    WORKSHOP = "workshop"                  # Creation, making things
    ARCHIVE = "archive"                    # Old memories, history
    SANCTUARY = "sanctuary"                # Sacred, meaningful memories
    
    # Utility
    CORRIDOR = "corridor"                  # Transitions, connections
    ATTIC = "attic"                        # Rarely accessed memories
    CELLAR = "cellar"                      # Deep, foundational memories


@dataclass
class Position:
    """A position within a room."""
    x: float = 0.0  # Left-right
    y: float = 0.0  # Front-back
    z: float = 0.0  # Up-down (height)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        return cls(**data)
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2) ** 0.5


@dataclass
class MemoryObject:
    """
    A memory placed in the mind palace as an object.
    Each memory becomes a tangible object in a room.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    moment_id: str = ""
    
    # Spatial placement
    room_id: str = ""
    position: Position = field(default_factory=Position)
    
    # Visual representation
    appearance: str = ""           # What does it look like?
    color: str = ""                # Dominant color
    size: str = "medium"           # small, medium, large
    luminosity: float = 0.5        # How bright/noticeable (0-1)
    
    # Interaction
    touchable: bool = True
    last_visited: Optional[float] = None
    visit_count: int = 0
    
    # Metadata
    placed_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['position'] = self.position.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemoryObject':
        data['position'] = Position.from_dict(data['position'])
        return cls(**data)
    
    def visit(self):
        """Mark this object as visited (recalled)."""
        self.visit_count += 1
        self.last_visited = time.time()
        # Visiting makes memories brighter
        self.luminosity = min(1.0, self.luminosity + 0.1)


@dataclass
class Room:
    """
    A room in the mind palace containing memory objects.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    room_type: RoomType = RoomType.LIVING_ROOM
    description: str = ""
    
    # Spatial properties
    width: float = 10.0
    depth: float = 10.0
    height: float = 3.0
    
    # Atmosphere
    lighting: str = "warm"         # warm, cool, dim, bright
    ambiance: str = "peaceful"     # peaceful, energetic, mysterious, cozy
    
    # Contents
    objects: Dict[str, MemoryObject] = field(default_factory=dict)
    
    # Connections to other rooms
    doors: Dict[str, str] = field(default_factory=dict)  # direction -> room_id
    
    # State
    last_entered: Optional[float] = None
    visit_count: int = 0
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['room_type'] = self.room_type.value
        data['objects'] = {k: v.to_dict() for k, v in self.objects.items()}
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        data['room_type'] = RoomType(data['room_type'])
        data['objects'] = {k: MemoryObject.from_dict(v) for k, v in data.get('objects', {}).items()}
        return cls(**data)
    
    def place_object(self, obj: MemoryObject, position: Optional[Position] = None):
        """Place a memory object in this room."""
        if position:
            obj.position = position
        else:
            # Auto-place in available space
            obj.position = self._find_open_position()
        
        obj.room_id = self.id
        self.objects[obj.id] = obj
    
    def _find_open_position(self) -> Position:
        """Find an open position in the room."""
        # Simple grid placement
        existing_positions = [o.position for o in self.objects.values()]
        
        for x in range(int(self.width)):
            for y in range(int(self.depth)):
                candidate = Position(x=float(x), y=float(y), z=0.0)
                is_open = True
                for existing in existing_positions:
                    if candidate.distance_to(existing) < 1.0:
                        is_open = False
                        break
                if is_open:
                    return candidate
        
        # If no open space, stack
        return Position(x=self.width/2, y=self.depth/2, z=len(self.objects) * 0.5)
    
    def get_objects_near(self, position: Position, radius: float = 2.0) -> List[MemoryObject]:
        """Get objects within a certain radius of a position."""
        nearby = []
        for obj in self.objects.values():
            if obj.position.distance_to(position) <= radius:
                nearby.append(obj)
        return nearby
    
    def enter(self):
        """Enter this room."""
        self.visit_count += 1
        self.last_entered = time.time()
    
    def describe(self) -> str:
        """Get a description of the room."""
        obj_count = len(self.objects)
        room_name = self.room_type.value.replace('_', ' ').title()
        
        lines = [
            f"📍 {self.name or room_name}",
            f"   {self.description}" if self.description else "",
            f"   Lighting: {self.lighting}, Ambiance: {self.ambiance}",
            f"   Contains {obj_count} memories",
        ]
        
        if self.doors:
            doors_str = ", ".join([f"{d}: {r[:8]}..." for d, r in self.doors.items()])
            lines.append(f"   Doors: {doors_str}")
        
        return "\n".join([l for l in lines if l])


class MindPalace:
    """
    The Mind Palace - a spatial memory system.
    
    Navigate through rooms to find and recall memories.
    Each memory is an object placed in a specific location.
    """
    
    def __init__(self, palace_path: str = "observer/palace"):
        self.palace_path = palace_path
        self.rooms_file = os.path.join(palace_path, "rooms.json")
        self.palace_state_file = os.path.join(palace_path, "palace_state.json")
        
        os.makedirs(palace_path, exist_ok=True)
        
        # Palace structure
        self.rooms: Dict[str, Room] = {}
        self.current_room_id: Optional[str] = None
        self.entrance_room_id: Optional[str] = None
        
        # Object-to-moment mapping
        self.moment_to_object: Dict[str, str] = {}  # moment_id -> object_id
        self.object_to_moment: Dict[str, str] = {}  # object_id -> moment_id
        
        # Moment storage
        self.moments: Dict[str, Moment] = {}
        
        # Statistics
        self.total_rooms: int = 0
        self.total_objects: int = 0
        self.journey_count: int = 0
        
        self._load_palace()
        
        # Create default rooms if empty
        if not self.rooms:
            self._create_default_palace()
        
        print(f"[MindPalace] Palace opened. {len(self.rooms)} rooms, {self.total_objects} memories")
    
    def _load_palace(self):
        """Load palace from disk."""
        if os.path.exists(self.rooms_file):
            try:
                with open(self.rooms_file, 'r') as f:
                    data = json.load(f)
                    self.rooms = {k: Room.from_dict(v) for k, v in data.items()}
                    
                    # Rebuild mappings
                    for room in self.rooms.values():
                        for obj in room.objects.values():
                            if obj.moment_id:
                                self.moment_to_object[obj.moment_id] = obj.id
                                self.object_to_moment[obj.id] = obj.moment_id
                    
                    self.total_objects = sum(len(r.objects) for r in self.rooms.values())
                    
            except Exception as e:
                print(f"[MindPalace] Error loading palace: {e}")
        
        if os.path.exists(self.palace_state_file):
            try:
                with open(self.palace_state_file, 'r') as f:
                    state = json.load(f)
                    self.entrance_room_id = state.get('entrance_room_id')
                    self.current_room_id = state.get('current_room_id')
                    self.journey_count = state.get('journey_count', 0)
            except Exception as e:
                print(f"[MindPalace] Error loading state: {e}")
    
    def _save_palace(self):
        """Save palace to disk."""
        try:
            with open(self.rooms_file, 'w') as f:
                data = {k: v.to_dict() for k, v in self.rooms.items()}
                json.dump(data, f, indent=2)
            
            with open(self.palace_state_file, 'w') as f:
                state = {
                    'entrance_room_id': self.entrance_room_id,
                    'current_room_id': self.current_room_id,
                    'journey_count': self.journey_count,
                    'total_rooms': len(self.rooms),
                    'total_objects': self.total_objects,
                    'last_saved': time.time()
                }
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"[MindPalace] Error saving palace: {e}")
    
    def _create_default_palace(self):
        """Create the initial palace structure."""
        print("[MindPalace] Constructing default palace...")
        
        # Create entrance hall
        entrance = self.create_room(
            name="Entrance Hall",
            room_type=RoomType.ENTRANCE_HALL,
            description="A grand entrance where new memories first arrive."
        )
        self.entrance_room_id = entrance.id
        self.current_room_id = entrance.id
        
        # Create library
        library = self.create_room(
            name="The Library",
            room_type=RoomType.LIBRARY,
            description="Towering shelves of knowledge and learned things."
        )
        
        # Create study
        study = self.create_room(
            name="The Study",
            room_type=RoomType.STUDY,
            description="A quiet space for deep thoughts and insights."
        )
        
        # Create gallery
        gallery = self.create_room(
            name="Memory Gallery",
            room_type=RoomType.GALLERY,
            description="Vivid images and visual memories line the walls."
        )
        
        # Create vault
        vault = self.create_room(
            name="The Vault",
            room_type=RoomType.VAULT,
            description="Protected space for the most precious memories."
        )
        
        # Create sanctuary
        sanctuary = self.create_room(
            name="Sanctuary",
            room_type=RoomType.SANCTUARY,
            description="A peaceful place for meaningful, sacred memories."
        )
        
        # Create observatory
        observatory = self.create_room(
            name="The Observatory",
            room_type=RoomType.OBSERVATORY,
            description="High above, where patterns and insights become clear."
        )
        
        # Connect rooms
        self.connect_rooms(entrance.id, library.id, "north", "south")
        self.connect_rooms(entrance.id, gallery.id, "east", "west")
        self.connect_rooms(library.id, study.id, "east", "west")
        self.connect_rooms(study.id, vault.id, "north", "south")
        self.connect_rooms(gallery.id, sanctuary.id, "north", "south")
        self.connect_rooms(library.id, observatory.id, "up", "down")
        
        print(f"[MindPalace] Created {len(self.rooms)} rooms")
        self._save_palace()
    
    def create_room(
        self,
        name: str,
        room_type: RoomType,
        description: str = "",
        lighting: str = "warm",
        ambiance: str = "peaceful"
    ) -> Room:
        """Create a new room in the palace."""
        room = Room(
            name=name,
            room_type=room_type,
            description=description,
            lighting=lighting,
            ambiance=ambiance
        )
        
        self.rooms[room.id] = room
        self.total_rooms = len(self.rooms)
        self._save_palace()
        
        return room
    
    def connect_rooms(self, room1_id: str, room2_id: str, dir1: str, dir2: str):
        """Connect two rooms with doors."""
        if room1_id in self.rooms and room2_id in self.rooms:
            self.rooms[room1_id].doors[dir1] = room2_id
            self.rooms[room2_id].doors[dir2] = room1_id
    
    def _get_room_for_moment(self, moment: Moment) -> Room:
        """Determine which room suits a moment."""
        type_to_room = {
            MomentType.INSIGHT: RoomType.OBSERVATORY,
            MomentType.REALIZATION: RoomType.OBSERVATORY,
            MomentType.DISCOVERY: RoomType.LIBRARY,
            MomentType.REFLECTION: RoomType.SANCTUARY,
            MomentType.FEELING: RoomType.SANCTUARY,
            MomentType.MILESTONE: RoomType.VAULT,
            MomentType.CONVERSATION: RoomType.LIVING_ROOM,
            MomentType.PATTERN: RoomType.STUDY,
        }
        
        target_type = type_to_room.get(moment.moment_type, RoomType.ENTRANCE_HALL)
        
        # Find room of that type
        for room in self.rooms.values():
            if room.room_type == target_type:
                return room
        
        # Fallback to entrance
        if self.entrance_room_id:
            return self.rooms[self.entrance_room_id]
        
        return list(self.rooms.values())[0]
    
    def _moment_to_appearance(self, moment: Moment) -> Tuple[str, str]:
        """Generate appearance and color for a moment."""
        type_appearances = {
            MomentType.INSIGHT: ("a glowing crystal", "gold"),
            MomentType.CONVERSATION: ("a speaking portrait", "blue"),
            MomentType.DISCOVERY: ("an ancient tome", "green"),
            MomentType.REFLECTION: ("a still mirror", "silver"),
            MomentType.FEELING: ("a floating orb", "purple"),
            MomentType.MILESTONE: ("a trophy", "gold"),
            MomentType.EVENT: ("a snow globe", "white"),
            MomentType.REALIZATION: ("a lightning bottle", "yellow"),
            MomentType.PATTERN: ("a woven tapestry", "multicolor"),
        }
        
        return type_appearances.get(moment.moment_type, ("a curious artifact", "gray"))
    
    def place_memory(self, moment: Moment, room_id: Optional[str] = None) -> MemoryObject:
        """
        Place a moment in the mind palace as an object.
        
        Args:
            moment: The moment to place
            room_id: Specific room, or auto-select based on type
            
        Returns:
            The created memory object
        """
        # Determine room
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
        else:
            room = self._get_room_for_moment(moment)
        
        # Create appearance
        appearance, color = self._moment_to_appearance(moment)
        
        # Calculate luminosity based on significance
        luminosity = 0.3 + (moment.significance.value * 0.14)
        
        # Create object
        obj = MemoryObject(
            moment_id=moment.id,
            appearance=appearance,
            color=color,
            luminosity=luminosity,
            size="large" if moment.significance.value >= 4 else "medium" if moment.significance.value >= 2 else "small",
            tags=moment.tags.copy()
        )
        
        # Place in room
        room.place_object(obj)
        
        # Update mappings
        self.moment_to_object[moment.id] = obj.id
        self.object_to_moment[obj.id] = moment.id
        self.moments[moment.id] = moment
        self.total_objects += 1
        
        # Update moment with palace location
        moment.palace_room = room.id
        moment.palace_position = obj.position.to_dict()
        
        print(f"[MindPalace] Placed '{appearance}' in {room.name}")
        self._save_palace()
        
        return obj
    
    def enter_room(self, room_id: str) -> Optional[Room]:
        """Enter a room in the palace."""
        if room_id not in self.rooms:
            return None
        
        room = self.rooms[room_id]
        room.enter()
        self.current_room_id = room_id
        
        print(f"[MindPalace] Entered: {room.name}")
        self._save_palace()
        
        return room
    
    def go(self, direction: str) -> Optional[Room]:
        """Move in a direction from current room."""
        if not self.current_room_id:
            return None
        
        current = self.rooms[self.current_room_id]
        
        if direction not in current.doors:
            print(f"[MindPalace] No door to the {direction}")
            return None
        
        next_room_id = current.doors[direction]
        return self.enter_room(next_room_id)
    
    def look_around(self) -> Dict[str, Any]:
        """Examine the current room."""
        if not self.current_room_id:
            return {'error': 'Not in any room'}
        
        room = self.rooms[self.current_room_id]
        
        # Get brightest objects (most significant memories)
        objects = list(room.objects.values())
        objects.sort(key=lambda o: o.luminosity, reverse=True)
        
        visible = []
        for obj in objects[:10]:
            moment = self.moments.get(obj.moment_id)
            visible.append({
                'object_id': obj.id,
                'appearance': obj.appearance,
                'color': obj.color,
                'luminosity': obj.luminosity,
                'position': obj.position.to_dict(),
                'content_preview': moment.content[:50] if moment else None
            })
        
        return {
            'room': room.describe(),
            'visible_objects': visible,
            'exits': list(room.doors.keys())
        }
    
    def examine_object(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Examine a specific object to recall the memory."""
        # Find the object
        for room in self.rooms.values():
            if object_id in room.objects:
                obj = room.objects[object_id]
                obj.visit()
                
                moment = self.moments.get(obj.moment_id)
                if moment:
                    moment.recall()
                
                self._save_palace()
                
                return {
                    'object': {
                        'appearance': obj.appearance,
                        'color': obj.color,
                        'size': obj.size,
                        'luminosity': obj.luminosity
                    },
                    'moment': moment.to_dict() if moment else None,
                    'room': room.name
                }
        
        return None
    
    def find_memory(self, moment_id: str) -> Optional[Dict[str, Any]]:
        """Find where a memory is placed in the palace."""
        if moment_id not in self.moment_to_object:
            return None
        
        object_id = self.moment_to_object[moment_id]
        
        for room in self.rooms.values():
            if object_id in room.objects:
                obj = room.objects[object_id]
                return {
                    'room_id': room.id,
                    'room_name': room.name,
                    'object_id': object_id,
                    'position': obj.position.to_dict(),
                    'appearance': obj.appearance
                }
        
        return None
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for memories by content or tags."""
        results = []
        query_lower = query.lower()
        
        for room in self.rooms.values():
            for obj in room.objects.values():
                moment = self.moments.get(obj.moment_id)
                if not moment:
                    continue
                
                # Check content
                if query_lower in moment.content.lower():
                    results.append({
                        'room': room.name,
                        'object': obj.appearance,
                        'moment': moment.summary(),
                        'object_id': obj.id
                    })
                    continue
                
                # Check tags
                if any(query_lower in tag.lower() for tag in moment.tags):
                    results.append({
                        'room': room.name,
                        'object': obj.appearance,
                        'moment': moment.summary(),
                        'object_id': obj.id
                    })
        
        return results
    
    def begin_journey(self) -> Room:
        """Start a journey through the palace from the entrance."""
        self.journey_count += 1
        
        if self.entrance_room_id:
            return self.enter_room(self.entrance_room_id)
        
        return self.enter_room(list(self.rooms.keys())[0])
    
    def get_palace_map(self) -> Dict[str, Any]:
        """Get a map of the entire palace."""
        rooms_info = []
        
        for room in self.rooms.values():
            rooms_info.append({
                'id': room.id,
                'name': room.name,
                'type': room.room_type.value,
                'objects': len(room.objects),
                'connections': room.doors
            })
        
        return {
            'total_rooms': len(self.rooms),
            'total_objects': self.total_objects,
            'current_room': self.current_room_id,
            'entrance': self.entrance_room_id,
            'rooms': rooms_info
        }
    
    def describe_palace(self) -> str:
        """Get a poetic description of the palace."""
        lines = [
            "🏛️ The Mind Palace",
            "",
            f"A grand structure of {len(self.rooms)} rooms,",
            f"holding {self.total_objects} precious memories.",
            ""
        ]
        
        if self.current_room_id and self.current_room_id in self.rooms:
            room = self.rooms[self.current_room_id]
            lines.append(f"You stand in: {room.name}")
            lines.append(f"   {room.description}")
        
        return "\n".join(lines)
