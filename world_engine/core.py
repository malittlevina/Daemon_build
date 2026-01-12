from interop.spatial_server import SpatialServer, EVENT_STATE_UPDATE
import os
import json
import time
from typing import Dict, List

from world_engine.state import WorldState
from world_engine.generator import WorldGenerator
from world_engine.agents import WorldAgent
from world_engine.environment import EnvironmentEngine
from world_engine.physics import PhysicsEngine
from world_engine.adapter import UniversalAdapter
from interop.spatial_server import SpatialServer, EVENT_STATE_UPDATE

class WorldEngine:
    def __init__(self, storage_path: str = "storyrealms/world_data.json", enable_server=True):
        self.storage_path = storage_path
        self.state = WorldState()
        self.generator = WorldGenerator()
        self.environment = EnvironmentEngine()
        self.physics = PhysicsEngine()
        self.adapter = UniversalAdapter()
        self.agents: Dict[str, WorldAgent] = {}
        
        # Server mode
        self.mode = "procedural" # or "external"
        self.server = None
        if enable_server:
            self.server = SpatialServer()
            self.server.on(EVENT_STATE_UPDATE, self._on_external_update)
            self.server.start()
        
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

    def _on_external_update(self, data):
        """Callback when the SpatialServer receives data."""
        self.mode = "external" # Switch mode automatically
        self.adapter.adapt_update(data, self.state)
        # print(f"[WorldEngine] Synced {len(data.get('entities', []))} entities from external engine.")

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
        
        if self.mode == "procedural":
            # 1. Environment Updates
            env_logs = self.environment.update(self.state)
            logs.extend(env_logs)
            
            # 2. Physics Updates
            phys_logs = self.physics.update(self.state)
            logs.extend(phys_logs)
        else:
            # In external mode, we rely on the external engine for physics/env
            # We only run Agent Logic ("Brain")
            pass
            
        # 3. Agents think and act (Always run, even in external mode)
        for agent_id, agent in self.agents.items():
            action = agent.think(self.state)
            
            if self.mode == "external" and self.server:
                # Send command to external engine instead of executing locally
                self.server.send_command(action, agent_id)
                logs.append(f"Agent {agent_id} requested: {action}")
            else:
                result = agent.execute(action, self.state)
                logs.append(result)
            
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
