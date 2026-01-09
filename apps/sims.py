from core.module import Module
import random
import time

class SimController(Module):
    """Manages NPC agents with Needs and Goals."""
    def __init__(self, kernel):
        super().__init__(kernel)
        self.agents = [] # List of entity UIDs

    def initialize(self):
        self.kernel.log("SimController", "Initialized.")

    def start(self):
        scheduler = self.kernel.get_module("scheduler")
        if scheduler:
            scheduler.schedule_interval(5, "sim_update", self.update_sims)

    def stop(self):
        pass

    def spawn_agent(self, name):
        world = self.kernel.get_module("world")
        if not world: return "World Engine not found."
        
        uid = world.create_object(name, position=(0, 5, 0))
        world.add_physics(uid, collider_size=(0.8, 1.8, 0.8))
        world.add_semantic_material(uid, "flesh", properties=["living", "hungry"])
        
        # Attach AI Script
        script = """
if "hunger" not in state: state["hunger"] = 0
state["hunger"] += 1
if state["hunger"] > 20:
    print(f"{name} is starving!")
    # Simple behavior: Random walk
    import random
    dx = random.choice([-1, 0, 1])
    dz = random.choice([-1, 0, 1])
    entity.get_component(Velocity).vector = [dx, 0, dz]
"""
        world.add_script(uid, script)
        self.agents.append(uid)
        return f"Spawned agent {name} ({uid})"

    def update_sims(self):
        # High level logic (Goal planning) could go here
        # The low-level logic runs in the ScriptSystem
        pass
