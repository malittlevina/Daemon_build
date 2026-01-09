import json
from .entities import Entity, AgentEntity

class RealmBuilder:
    def __init__(self, world_engine):
        self.world_engine = world_engine

    def generate_realm_from_prompt(self, name, prompt):
        """
        Simulates using an LLM to generate a full realm structure from a text prompt.
        In a real system, this would call `codex` or an API.
        Here we use procedural templates.
        """
        print(f"[RealmBuilder] Dreaming up '{name}' based on: {prompt}")
        
        description = f"A procedurally generated world based on concepts of: {prompt}"
        
        # Template selection based on keywords
        if "city" in prompt.lower():
            realm = self._template_city(name, description)
        elif "forest" in prompt.lower():
            realm = self._template_forest(name, description)
        elif "cyber" in prompt.lower() or "tech" in prompt.lower():
            realm = self._template_cyber(name, description)
        else:
            realm = self._template_generic(name, description)
            
        self.world_engine.save_realm(realm)
        return realm

    def _template_city(self, name, description):
        realm = self.world_engine.create_realm(name, description)
        
        structure = {
            "Root": {"type": "Plaza", "subregions": ["District_A", "District_B"]},
            "District_A": {"type": "Residential", "subregions": []},
            "District_B": {"type": "Commercial", "subregions": ["Market"]}
        }
        realm.state["structure"] = structure
        
        # Add Citizens
        realm.entities.append(AgentEntity("CityGuard_01", role="Guardian", location="Root").to_dict())
        realm.entities.append(AgentEntity("Architect_X", role="Builder", location="District_B").to_dict())
        
        return realm

    def _template_cyber(self, name, description):
        realm = self.world_engine.create_realm(name, description)
        
        structure = {
            "Root": {"type": "Mainframe", "subregions": ["Node_1", "Node_2", "Firewall"]},
            "Node_1": {"type": "DataBank", "subregions": []},
            "Firewall": {"type": "SecurityGate", "subregions": []}
        }
        realm.state["structure"] = structure
        
        # Add Cyber Agents
        realm.entities.append(AgentEntity("NetSec_Bot", role="Guardian", location="Firewall").to_dict())
        realm.entities.append(AgentEntity("Data_Miner", role="Cleaner", location="Node_1").to_dict())
        
        return realm

    def _template_forest(self, name, description):
        realm = self.world_engine.create_realm(name, description)
        structure = {
            "Root": {"type": "Clearing", "subregions": ["Thicket", "River"]},
            "Thicket": {"type": "DenseWoods", "subregions": []}
        }
        realm.state["structure"] = structure
        return realm

    def _template_generic(self, name, description):
        return self.world_engine.create_realm(name, description)
