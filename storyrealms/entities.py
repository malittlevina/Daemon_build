import random
import time

class Entity:
    def __init__(self, name, entity_type, location="Root", properties=None):
        self.name = name
        self.type = entity_type
        self.location = location
        self.properties = properties or {}
        self.id = f"{name}_{int(time.time()*1000)}"

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "properties": self.properties,
            "id": self.id
        }

    def update(self, world_context):
        """Base update method called every tick."""
        pass

class AgentEntity(Entity):
    def __init__(self, name, role="Observer", location="Root", properties=None):
        super().__init__(name, "Agent", location, properties)
        self.role = role
        self.state = "idle"
        self.inventory = []
        self.memory = []

    def update(self, world_context):
        # Basic AI Loop
        if self.role == "Guardian":
            self._patrol_logic(world_context)
        elif self.role == "Builder":
            self._builder_logic(world_context)
        elif self.role == "Cleaner":
            self._cleaner_logic(world_context)

    def _patrol_logic(self, context):
        # Simulate moving between regions
        if random.random() < 0.2:
            current_realm = context.get("current_realm")
            if current_realm:
                structure = current_realm.state.get("structure", {})
                possible_moves = list(structure.keys())
                if possible_moves:
                    new_loc = random.choice(possible_moves)
                    self.location = new_loc
                    self.state = f"Patrolling {new_loc}"
                    print(f"[Entity: {self.name}] Moved to {new_loc}")

    def _cleaner_logic(self, context):
        # Look for 'corrupt' or 'temp' artifacts and 'remove' them (logically)
        current_realm = context.get("current_realm")
        if current_realm and random.random() < 0.1:
            print(f"[Entity: {self.name}] Sweeping {self.location}...")

    def _builder_logic(self, context):
        # Randomly 'improves' descriptions (simulated)
        if random.random() < 0.05:
            print(f"[Entity: {self.name}] Inspecting structure at {self.location} for improvements.")

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "role": self.role,
            "state": self.state,
            "inventory": self.inventory
        })
        return d
