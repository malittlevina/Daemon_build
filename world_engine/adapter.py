from typing import Dict, Any, List
from world_engine.state import WorldState, Entity, Location

class UniversalAdapter:
    """
    Adapts external 3D engine data (JSON schema) into internal WorldState concepts.
    """
    def __init__(self):
        # Mappings of external types to internal logic
        self.type_map = {
            "PlayerCharacter": "NPC",
            "Bot": "NPC",
            "StaticMesh": "Item", # Default fallback
            "Tree": "Environment",
            "SpawnPoint": "Location"
        }
        
    def adapt_update(self, external_data: Dict[str, Any], current_state: WorldState):
        """
        Merges external data into the current WorldState.
        Expected Schema:
        {
            "entities": [ {"id": "1", "type": "Bot", "pos": [0,0,0], "props": {}} ],
            "global": { "time": 1200 }
        }
        """
        # 1. Adapt Entities
        ext_entities = external_data.get("entities", [])
        active_ids = []
        
        for ext_ent in ext_entities:
            eid = str(ext_ent.get("id"))
            active_ids.append(eid)
            
            # Map type
            ext_type = ext_ent.get("type", "Unknown")
            int_type = self.type_map.get(ext_type, "Item")
            
            # Get or Create
            if eid in current_state.entities:
                entity = current_state.entities[eid]
            else:
                entity = Entity(f"Ext_{ext_type}_{eid}", int_type)
                entity.id = eid # Force ID match
                current_state.add_entity(entity)
            
            # Update Properties
            entity.properties["position"] = ext_ent.get("pos", [0,0,0])
            entity.properties["rotation"] = ext_ent.get("rot", [0,0,0])
            entity.properties.update(ext_ent.get("props", {}))
            
            # Update Meta
            entity.name = ext_ent.get("name", entity.name)
            
        # 2. Sync globals
        ext_global = external_data.get("global", {})
        current_state.global_properties.update(ext_global)
        
        return active_ids
