from typing import Dict, List, Optional
from .entity import Entity, Creature, DaemonAvatar

class Location:
    def __init__(self, name: str, description: str):
        self.id = name.lower().replace(" ", "_")
        self.name = name
        self.description = description
        self.exits: Dict[str, str] = {}  # direction -> location_id
        self.entities: List[Entity] = []
        self.items: List[str] = []
        self.is_puzzle_solved = False

    def connect(self, direction: str, location_id: str):
        self.exits[direction] = location_id

    def add_entity(self, entity: Entity):
        self.entities.append(entity)
        entity.location_id = self.id

    def remove_entity(self, entity: Entity):
        if entity in self.entities:
            self.entities.remove(entity)
            entity.location_id = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "entities": [e.to_dict() for e in self.entities],
            "items": self.items,
            "is_puzzle_solved": self.is_puzzle_solved
        }

    @classmethod
    def from_dict(cls, data: Dict):
        loc = cls(data["name"], data["description"])
        loc.id = data["id"]
        loc.exits = data["exits"]
        loc.items = data["items"]
        loc.is_puzzle_solved = data.get("is_puzzle_solved", False)
        for e_data in data["entities"]:
            loc.entities.append(Entity.from_dict(e_data))
        return loc

class Zone:
    def __init__(self, name: str, theme: str):
        self.name = name
        self.theme = theme
        self.locations: Dict[str, Location] = {}
        self.start_location_id: Optional[str] = None

    def add_location(self, location: Location, is_start=False):
        self.locations[location.id] = location
        if is_start:
            self.start_location_id = location.id

    def get_location(self, location_id: str) -> Optional[Location]:
        return self.locations.get(location_id)

    def to_dict(self):
        return {
            "name": self.name,
            "theme": self.theme,
            "locations": {k: v.to_dict() for k, v in self.locations.items()},
            "start_location_id": self.start_location_id
        }

    @classmethod
    def from_dict(cls, data: Dict):
        zone = cls(data["name"], data["theme"])
        zone.start_location_id = data["start_location_id"]
        for k, v in data["locations"].items():
            zone.locations[k] = Location.from_dict(v)
        return zone

class Realm:
    def __init__(self, name: str):
        self.name = name
        self.zones: Dict[str, Zone] = {}
        self.current_zone_id: Optional[str] = None
        self.player_location_id: Optional[str] = None
        self.player_team: List[Creature] = []
        self.daemon_avatar: Optional[DaemonAvatar] = None

    def add_zone(self, zone: Zone, is_start=False):
        self.zones[zone.name] = zone
        if is_start:
            self.current_zone_id = zone.name

    def to_dict(self):
        return {
            "name": self.name,
            "current_zone": self.current_zone_id,
            "player_location": self.player_location_id,
            "zones": {k: v.to_dict() for k, v in self.zones.items()},
            "player_team": [c.to_dict() for c in self.player_team],
            "daemon_avatar": self.daemon_avatar.to_dict() if self.daemon_avatar else None
        }

    @classmethod
    def from_dict(cls, data: Dict):
        realm = cls(data["name"])
        realm.current_zone_id = data["current_zone"]
        realm.player_location_id = data["player_location"]
        
        for k, v in data["zones"].items():
            realm.zones[k] = Zone.from_dict(v)
            
        for c_data in data["player_team"]:
            realm.player_team.append(Creature.from_dict(c_data))
            
        if data["daemon_avatar"]:
            realm.daemon_avatar = DaemonAvatar.from_dict(data["daemon_avatar"])
            
        return realm
