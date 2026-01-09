import random
from typing import Dict, Any
from .base import MindModule

class CreativeModule(MindModule):
    def __init__(self):
        super().__init__("CreativeSpark")
        self.game_inspirations = [
            "What if we tried a stealth approach?",
            "Maybe we can negotiate?",
            "Let's use the environment to our advantage.",
            "Charge in with a battle cry!",
            "Distract them with a hologram."
        ]
        self.code_inspirations = [
            "We could refactor this using a Strategy pattern.",
            "Maybe a decorator would clean this up?",
            "How about we make it async for better performance?",
            "Let's add some colorful logging!",
            "What if we used a generator here?"
        ]

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        updates = {}
        user_input = context.get("user_input", "").lower()
        
        # 1. Game Creativity
        if "options" in context or "encounter" in context.get("event_type", ""):
            if "options" not in context:
                context["options"] = {}
            idea = random.choice(self.game_inspirations)
            updates["creative_suggestion"] = idea
            context["options"]["creative_solution"] = {
                "logic": 0.2, "emotion": 0.9, "intuition": 0.8
            }

        # 2. General/Coding Creativity
        if "code" in user_input or "feature" in user_input:
            idea = random.choice(self.code_inspirations)
            updates["creative_suggestion"] = idea
            
        return updates
