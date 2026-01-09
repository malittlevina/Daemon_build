import time

class PlayerEntity(Entity):
    def __init__(self, name, location="Root", properties=None, client_id=None):
        super().__init__(name, "Player", location, properties)
        self.client_id = client_id
        self.state = "active"
        self.inventory = []
        self.health = 100
        self.xp = 0

    def move(self, new_location, world_context):
        current_realm = world_context.get("current_realm")
        if not current_realm: return False
        
        structure = current_realm.state.get("structure", {})
        if new_location in structure:
            self.location = new_location
            print(f"[Player: {self.name}] Moved to {new_location}")
            return True
        return False

    def interact(self, target_name, world_context):
        # Find target in current location
        current_realm = world_context.get("current_realm")
        entities = current_realm.entities
        
        target = next((e for e in entities if e.get("name") == target_name and e.get("location") == self.location), None)
        
        if target:
            print(f"[Player: {self.name}] Interacted with {target_name}")
            return f"You interact with {target_name}. It seems to be a {target.get('type')}."
        return "Target not found here."

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "client_id": self.client_id,
            "state": self.state,
            "inventory": self.inventory,
            "health": self.health,
            "xp": self.xp
        })
        return d
