from core.module import Module
import random
import time

class Dreamer(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.is_dreaming = False

    def initialize(self):
        self.kernel.log("Dreamer", "Initialized. Waiting for sleep.")

    def start(self):
        scheduler = self.kernel.get_module("scheduler")
        if scheduler:
            # Dream every 2 minutes if idle
            scheduler.schedule_interval(120, "rem_cycle", self.dream)

    def stop(self):
        pass

    def dream(self):
        """Simulate a hypothetical scenario in the World Engine."""
        self.kernel.log("Dreamer", "Entering REM cycle...")
        
        world = self.kernel.get_module("world")
        graph = self.kernel.get_module("knowledge_graph")
        
        if not world or not graph: 
            return

        # 1. Pick a concept to test
        # We query the graph for facts. (Mocking query for now as graph might be empty)
        concepts = ["fire", "water", "paper", "stone"]
        
        concept_a = random.choice(concepts)
        concept_b = random.choice(concepts)
        
        self.kernel.log("Dreamer", f"Hypothesis: What happens if {concept_a} meets {concept_b}?")
        
        # 2. Setup Simulation
        # We spawn temporary entities far away from the main area
        sim_pos = (1000, 1000, 1000) 
        
        uid_a = world.create_object(f"Dream_{concept_a}", sim_pos)
        world.add_physics(uid_a, collider_size=(1,1,1))
        world.add_semantic_material(uid_a, concept_a, properties=["flammable"] if concept_a == "paper" else [])
        
        uid_b = world.create_object(f"Dream_{concept_b}", sim_pos) # Same pos = instant collision
        world.add_physics(uid_b, collider_size=(1,1,1))
        world.add_semantic_material(uid_b, concept_b, properties=["flammable"] if concept_b == "paper" else [])
        
        # 3. Observe (The SemanticSystem will trigger events)
        # In a real system, we'd listen for specific events correlated to these UIDs.
        # For now, we just let it run.
        
        # 4. Cleanup (Wake up)
        # We rely on the world engine to keep running. 
        # Ideally we'd delete them after a few seconds.
        
        self.kernel.log("Dreamer", "Dream complete.")
