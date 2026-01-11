from .base_region import BrainRegion

class FrontalCortex(BrainRegion):
    """
    Responsible for Logic, Planning, and Decision Making.
    Acts as the coordinator or 'Executive Function'.
    """
    def __init__(self):
        super().__init__("FrontalCortex", "Executive Function and Logic")

    def process(self, input_data, context=None, **kwargs):
        print(f"[{self.name}] Analyzing input: {input_data} with context: {context}")
        # Placeholder for reasoning models (e.g., Chain of Thought logic)
        decision = f"Decided to act on: {input_data}"
        return decision
