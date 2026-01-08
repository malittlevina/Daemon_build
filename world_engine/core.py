import os
import json
import time
from typing import Dict, List

from world_engine.state import WorldState
from world_engine.generator import WorldGenerator
from world_engine.agents import WorldAgent

class WorldEngine:
    def __init__(self, storage_path: str = "storyrealms/world_data.json"):
        self.storage_path = storage_path
        self.state = WorldState()
        self.generator = WorldGenerator()
        self.agents: Dict[str, WorldAgent] = {}
        
        # Load existing state if available
        if os.path.exists(self.storage_path):
            try:
                self.state = WorldState.load(self.storage_path)
                print(f"[WorldEngine] Loaded state from {self.storage_path}")
                # Re-initialize agents for existing entities
                for ent_id, ent in self.state.entities.items():
                    if ent.entity_type == "NPC": # Only NPCs are agents for now
                        self.agents[ent_id] = WorldAgent(ent_id)
            except Exception as e:
                print(f"[WorldEngine] Failed to load state: {e}. Creating new world.")
                self.create_new_world()
        else:
            print("[WorldEngine] No existing world found. Creating new world.")
            self.create_new_world()

    def create_new_world(self):
        self.state = WorldState()
        self.generator.populate_world(self.state)
        # Initialize agents
        for ent_id, ent in self.state.entities.items():
            if ent.entity_type == "NPC":
                self.agents[ent_id] = WorldAgent(ent_id)
        self.save_world()

    def save_world(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.state.save(self.storage_path)

    def step(self):
        """Advance the world simulation by one tick."""
        self.state.time += 1.0
        logs = []
        
        # 1. Agents think and act
        for agent_id, agent in self.agents.items():
            action = agent.think(self.state)
            result = agent.execute(action, self.state)
            logs.append(result)
            
        # 2. Physics/Environment updates (placeholder)
        # e.g., weather changes, decay
        
        self.save_world()
        return logs

    def get_world_summary(self):
        return {
            "time": self.state.time,
            "location_count": len(self.state.locations),
            "entity_count": len(self.state.entities),
            "locations": [loc.name for loc in self.state.locations.values()]
        }
    
    def get_location_info(self, location_name_or_id: str):
        # Search by ID first
        if location_name_or_id in self.state.locations:
            return self.state.locations[location_name_or_id].to_dict()
            
        # Search by name
        for loc in self.state.locations.values():
            if loc.name == location_name_or_id:
                return loc.to_dict()
        return None
