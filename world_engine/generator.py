import random
from typing import List, Dict, Any
from world_engine.state import WorldState, Location, Entity

class WorldGenerator:
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
        
        self.biomes = ["Forest", "Desert", "City", "Mountain", "Space Station", "Ocean"]
        self.adjectives = ["Ancient", "Futuristic", "Haunted", "Serene", "Bustling", "Desolate"]
        
    def generate_location(self) -> Location:
        biome = random.choice(self.biomes)
        adj = random.choice(self.adjectives)
        name = f"{adj} {biome}"
        description = f"A {adj.lower()} {biome.lower()} with unique features."
        
        properties = {
            "temperature": random.randint(-20, 40),
            "humidity": random.randint(0, 100),
            "danger_level": random.randint(1, 10),
            "weather": random.choice(["Clear", "Rain", "Fog", "Clear", "Clear"]),
            "light_level": 1.0
        }
        
        return Location(name, description, properties)

    def generate_entity(self, location_id: str = None) -> Entity:
        types = ["NPC", "Item", "Creature"]
        entity_type = random.choice(types)
        
        names = {
            "NPC": ["Guard", "Merchant", "Traveler", "Scientist"],
            "Item": ["Sword", "Datapad", "Potion", "Artifact"],
            "Creature": ["Wolf", "Droid", "Alien", "Spirit"]
        }
        
        name = random.choice(names[entity_type]) + f" {random.randint(1, 100)}"
        
        properties = {
            "value": random.randint(1, 100),
            "weight": random.randint(1, 50),
            "mass": random.uniform(10.0, 100.0),
            "velocity": [0.0, 0.0, 0.0],
            "position": [random.uniform(-10, 10), 0.0, random.uniform(-10, 10)]
        }
        
        entity = Entity(name, entity_type, properties)
        entity.location_id = location_id
        return entity

    def populate_world(self, state: WorldState, num_locations: int = 5):
        locations = []
        for _ in range(num_locations):
            loc = self.generate_location()
            state.add_location(loc)
            locations.append(loc)
        
        # Connect locations linearly for simplicity, can be a graph
        for i in range(len(locations) - 1):
            locations[i].connect(locations[i+1].id)
            locations[i+1].connect(locations[i].id)
            
        # Add entities
        for loc in locations:
            num_entities = random.randint(1, 3)
            for _ in range(num_entities):
                ent = self.generate_entity(loc.id)
                state.add_entity(ent)
