from typing import Dict, Any
from .base import MindModule
from ..decision_matrix import DecisionMatrix

class StrategyModule(MindModule):
    def __init__(self):
        super().__init__("StrategyPlanner")
        self.matrix = DecisionMatrix()

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # If there are options to choose from, use the matrix
        options = context.get("options")
        if options and isinstance(options, dict):
            choice = self.matrix.choose(options)
            return {"selected_option": choice}
            
        return {}
