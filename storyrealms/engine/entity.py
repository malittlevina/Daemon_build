import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Stats:
    hp: int
    max_hp: int
    energy: int
    max_energy: int
    attack: int
    defense: int
    speed: int

@dataclass
class Move:
    name: str
    damage: int
    cost: int
    description: str
    effect: Optional[str] = None

class Entity:
    def __init__(self, name: str, description: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.location_id: Optional[str] = None
        self.tags: List[str] = []

    def to_dict(self):
        return {
            "type": "entity",
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location_id": self.location_id,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict):
        # Dispatch to subclass if needed based on type
        if data.get("type") == "creature":
            return Creature.from_dict(data)
        if data.get("type") == "daemon_avatar":
            return DaemonAvatar.from_dict(data)
            
        entity = cls(data["name"], data["description"])
        entity.id = data["id"]
        entity.location_id = data["location_id"]
        entity.tags = data.get("tags", [])
        return entity

class Creature(Entity):
    def __init__(self, name: str, description: str, creature_type: str, stats: Stats):
        super().__init__(name, description)
        self.creature_type = creature_type
        self.stats = stats
        self.moves: List[Move] = []
        self.level = 1
        self.experience = 0

    def add_move(self, move: Move):
        self.moves.append(move)

    def take_damage(self, amount: int):
        self.stats.hp = max(0, self.stats.hp - amount)
        return self.stats.hp == 0

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "type": "creature",
            "creature_type": self.creature_type,
            "stats": self.stats.__dict__,
            "moves": [m.__dict__ for m in self.moves],
            "level": self.level,
            "experience": self.experience
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict):
        stats_data = data["stats"]
        stats = Stats(**stats_data)
        creature = cls(data["name"], data["description"], data["creature_type"], stats)
        creature.id = data["id"]
        creature.location_id = data["location_id"]
        creature.tags = data.get("tags", [])
        creature.level = data["level"]
        creature.experience = data["experience"]
        
        for m_data in data["moves"]:
            creature.add_move(Move(**m_data))
            
        return creature

class DaemonAvatar(Entity):
    def __init__(self, name: str, description: str = "Your loyal digital companion made manifest."):
        super().__init__(name, description)
        self.sync_rate = 100.0  # Percentage of connection to the core Daemon
        self.abilities: List[str] = ["Analyze", "Hack", "Shield"]

    def analyze_target(self, target: Entity) -> str:
        return f"Analysis of {target.name}: {target.description}"

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "type": "daemon_avatar",
            "sync_rate": self.sync_rate,
            "abilities": self.abilities
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict):
        avatar = cls(data["name"], data["description"])
        avatar.id = data["id"]
        avatar.location_id = data["location_id"]
        avatar.tags = data.get("tags", [])
        avatar.sync_rate = data["sync_rate"]
        avatar.abilities = data["abilities"]
        return avatar
