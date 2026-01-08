import uuid
from typing import Dict, List, Optional, Any
import json
import time

class Entity:
    def __init__(self, name: str, entity_type: str, properties: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.entity_type = entity_type
        self.properties = properties or {}
        self.location_id: Optional[str] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "location_id": self.location_id
        }

class Location:
    def __init__(self, name: str, description: str, properties: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.properties = properties or {}
        self.connected_location_ids: List[str] = []
        self.entities: List[str] = []

    def connect(self, location_id: str):
        if location_id not in self.connected_location_ids:
            self.connected_location_ids.append(location_id)

    def add_entity(self, entity_id: str):
        if entity_id not in self.entities:
            self.entities.append(entity_id)
            
    def remove_entity(self, entity_id: str):
        if entity_id in self.entities:
            self.entities.remove(entity_id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "connected_location_ids": self.connected_location_ids,
            "entities": self.entities
        }

class WorldState:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.entities: Dict[str, Entity] = {}
        self.global_properties: Dict[str, Any] = {}
        self.time: float = 0.0

    def add_location(self, location: Location):
        self.locations[location.id] = location

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity
        if entity.location_id and entity.location_id in self.locations:
            self.locations[entity.location_id].add_entity(entity.id)

    def move_entity(self, entity_id: str, target_location_id: str):
        if entity_id not in self.entities or target_location_id not in self.locations:
            return False
        
        entity = self.entities[entity_id]
        if entity.location_id:
            old_loc = self.locations[entity.location_id]
            old_loc.remove_entity(entity_id)
        
        entity.location_id = target_location_id
        new_loc = self.locations[target_location_id]
        new_loc.add_entity(entity_id)
        return True

    def to_dict(self):
        return {
            "locations": {k: v.to_dict() for k, v in self.locations.items()},
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "global_properties": self.global_properties,
            "time": self.time
        }

    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str):
        state = cls()
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for loc_id, loc_data in data["locations"].items():
            loc = Location(loc_data["name"], loc_data["description"], loc_data.get("properties"))
            loc.id = loc_id
            loc.connected_location_ids = loc_data.get("connected_location_ids", [])
            loc.entities = loc_data.get("entities", [])
            state.locations[loc_id] = loc
            
        for ent_id, ent_data in data["entities"].items():
            ent = Entity(ent_data["name"], ent_data["entity_type"], ent_data.get("properties"))
            ent.id = ent_id
            ent.location_id = ent_data.get("location_id")
            state.entities[ent_id] = ent
            
        state.global_properties = data.get("global_properties", {})
        state.time = data.get("time", 0.0)
        return state
