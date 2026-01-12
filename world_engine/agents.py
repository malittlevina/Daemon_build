from typing import List
import random
from world_engine.state import WorldState, Entity

class WorldAgent:
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
    
    def think(self, state: WorldState) -> str:
        """Decide on an action based on the world state."""
        entity = state.entities.get(self.entity_id)
        if not entity:
            return "Do nothing (existential crisis)"
        
        location = state.locations.get(entity.location_id)
        
        # Simple behavior loop
        action_roll = random.random()
        
        if action_roll < 0.3:
            # Move
            if location and location.connected_location_ids:
                target_id = random.choice(location.connected_location_ids)
                target_loc = state.locations[target_id]
                return f"move_to:{target_id}"
        elif action_roll < 0.6:
            # Interact
            return "interact:environment"
        else:
            # Idle
            return "idle"

    def execute(self, action: str, state: WorldState) -> str:
        if action.startswith("move_to:"):
            target_id = action.split(":")[1]
            if state.move_entity(self.entity_id, target_id):
                target_name = state.locations[target_id].name
                return f"Entity {self.entity_id} moved to {target_name}"
            else:
                return f"Entity {self.entity_id} failed to move."
        elif action == "idle":
             return f"Entity {self.entity_id} is waiting."
        else:
            return f"Entity {self.entity_id} performed {action}"
