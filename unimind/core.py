from unimind.brain_regions import FrontalCortex, Hippocampus, BrocasArea, OccipitalLobe, TemporalLobe

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
