import json
import os
import time

class Realm:
    def __init__(self, name, description, rules=None, entities=None):
        self.name = name
        self.description = description
        self.rules = rules or {}
        self.entities = entities or []
        self.state = {}

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "rules": self.rules,
            "entities": self.entities,
            "state": self.state
        }

    @classmethod
    def from_dict(cls, data):
        realm = cls(
            name=data["name"],
            description=data.get("description", ""),
            rules=data.get("rules", {}),
            entities=data.get("entities", [])
        )
        realm.state = data.get("state", {})
        return realm

class StoryRealmsEngine:
    def __init__(self, storage_path="storyrealms/data"):
        self.storage_path = storage_path
        self.current_realm = None
        self.realms = {}
        self.ensure_storage()
        self.load_realms()
        
        # Default realm if none exists
        if not self.realms:
            self.create_realm("Nexus", "The central hub of all realities.")
            self.enter_realm("Nexus")

    def ensure_storage(self):
        os.makedirs(self.storage_path, exist_ok=True)

    def load_realms(self):
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                path = os.path.join(self.storage_path, filename)
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        realm = Realm.from_dict(data)
                        self.realms[realm.name] = realm
                except Exception as e:
                    print(f"[StoryRealms] Failed to load realm {filename}: {e}")

    def save_realm(self, realm):
        filename = f"{realm.name.lower().replace(' ', '_')}.json"
        path = os.path.join(self.storage_path, filename)
        with open(path, "w") as f:
            json.dump(realm.to_dict(), f, indent=2)

    def create_realm(self, name, description, rules=None):
        if name in self.realms:
            return self.realms[name]
        
        realm = Realm(name, description, rules)
        self.realms[name] = realm
        self.save_realm(realm)
        print(f"[StoryRealms] Created new realm: {name}")
        return realm

    def enter_realm(self, name):
        if name not in self.realms:
            print(f"[StoryRealms] Realm '{name}' does not exist.")
            return False
        
        self.current_realm = self.realms[name]
        print(f"[StoryRealms] Entered realm: {name}")
        return True

    def get_current_context(self):
        if not self.current_realm:
            return "Void"
        return f"Realm: {self.current_realm.name}\nDescription: {self.current_realm.description}"

    def trigger_event(self, event_description):
        if not self.current_realm:
            return
        
        timestamp = time.ctime()
        event_log = f"[{timestamp}] {event_description}"
        
        # Store in realm state history
        if "history" not in self.current_realm.state:
            self.current_realm.state["history"] = []
        self.current_realm.state["history"].append(event_log)
        
        self.save_realm(self.current_realm)
        print(f"[StoryRealms] Event in {self.current_realm.name}: {event_description}")
