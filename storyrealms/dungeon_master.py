import random
import uuid

class Quest:
    def __init__(self, title, description, reward=None):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.reward = reward or "Experience"
        self.steps = []
        self.status = "active"  # active, completed, failed

    def add_step(self, description, target_location=None, target_entity=None):
        self.steps.append({
            "description": description,
            "target_location": target_location,
            "target_entity": target_entity,
            "completed": False
        })

    def check_progress(self, current_location, interacted_entity=None):
        for step in self.steps:
            if not step["completed"]:
                # Check location match
                loc_match = step["target_location"] is None or step["target_location"] == current_location
                # Check entity match
                ent_match = step["target_entity"] is None or step["target_entity"] == interacted_entity
                
                if loc_match and ent_match:
                    step["completed"] = True
                    return f"Step Completed: {step['description']}"
        
        if all(s["completed"] for s in self.steps):
            self.status = "completed"
            return f"Quest Completed: {self.title}!"
            
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reward": self.reward,
            "steps": self.steps,
            "status": self.status
        }

class DungeonMaster:
    def __init__(self, world_engine):
        self.world_engine = world_engine

    def generate_quest(self, realm_name):
        if realm_name not in self.world_engine.realms:
            return None
            
        realm = self.world_engine.realms[realm_name]
        structure = realm.state.get("structure", {})
        regions = list(structure.keys())
        
        if not regions:
            return None

        # Simple Procedural Quest Generation
        quest_type = random.choice(["fetch", "explore", "hunt"])
        
        if quest_type == "fetch":
            target_region = random.choice(regions)
            item = f"Artifact_{random.randint(100,999)}"
            title = f"Retrieve the {item}"
            desc = f"Go to {target_region} and find the {item}."
            quest = Quest(title, desc)
            quest.add_step(f"Travel to {target_region}", target_location=target_region)
            quest.add_step(f"Pick up {item}", target_location=target_region) # Abstract step
            
        elif quest_type == "explore":
            target_region = random.choice(regions)
            title = f"Scout {target_region}"
            desc = f"We need intel on {target_region}. Go there."
            quest = Quest(title, desc)
            quest.add_step(f"Arrive at {target_region}", target_location=target_region)
            
        elif quest_type == "hunt":
            target_region = random.choice(regions)
            title = f"Clear out {target_region}"
            desc = f"Dangerous entities detected in {target_region}."
            quest = Quest(title, desc)
            quest.add_step(f"Defeat enemies in {target_region}", target_location=target_region)

        # Register quest in realm state
        if "quests" not in realm.state:
            realm.state["quests"] = []
        realm.state["quests"].append(quest.to_dict())
        self.world_engine.save_realm(realm)
        
        return quest

    def list_active_quests(self, realm_name):
        if realm_name not in self.world_engine.realms:
            return []
        realm = self.world_engine.realms[realm_name]
        return realm.state.get("quests", [])
