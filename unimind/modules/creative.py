import random
from typing import Dict, Any
from .base import MindModule

class CreativeModule(MindModule):
    def __init__(self):
        super().__init__("CreativeSpark")
        self.inspirations = [
            "What if we tried a stealth approach?",
            "Maybe we can negotiate?",
            "Let's use the environment to our advantage.",
            "Charge in with a battle cry!",
            "Distract them with a hologram."
        ]

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Creativity adds "wild" options or narrative flair
        updates = {}
        
        # Add a creative option if none exists
        if "options" not in context:
            context["options"] = {}
            
        # Propose a creative solution
        idea = random.choice(self.inspirations)
        updates["creative_suggestion"] = idea
        
        # Add a "creative" option to the decision matrix inputs
        # Assign high emotion/intuition weight
        context["options"]["creative_solution"] = {
            "logic": 0.2,
            "emotion": 0.9,
            "intuition": 0.8
        }
        
        return updates
