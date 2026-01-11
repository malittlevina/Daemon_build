from unimind.brain_regions import FrontalCortex, Hippocampus, BrocasArea, OccipitalLobe, TemporalLobe
from unimind.evolution import EvolutionEngine

class Unimind:
    def __init__(self):
        self.modules = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": []
        }
        
        # Initialize Brain Regions
        self.frontal_cortex = FrontalCortex()
        self.hippocampus = Hippocampus()
        self.brocas_area = BrocasArea()
        self.occipital_lobe = OccipitalLobe()
        self.temporal_lobe = TemporalLobe()
        
        self.regions = {
            "frontal": self.frontal_cortex,
            "hippocampus": self.hippocampus,
            "broca": self.brocas_area,
            "occipital": self.occipital_lobe,
            "temporal": self.temporal_lobe
        }
        
        # Initialize Evolution Engine
        self.evolution_engine = EvolutionEngine(self)
        
        print("[Unimind] Core initialized with Brain Regions.")

    def register(self, type, module):
        if type in self.modules:
            self.modules[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        # Use Frontal Cortex for reflection logic
        self.frontal_cortex.process("daily_reflection", context="self_improvement")
        
        for logic_module in self.modules["logic"]:
            logic_module.think()

    def evolve(self, interaction_data):
        self.evolution_engine.evolve(interaction_data)

    def learn(self, interaction_data):
        # Delegate learning to each brain region
        for region in self.regions.values():
            region.learn(interaction_data)
