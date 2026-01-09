from typing import Dict, Any
from .base import MindModule

class EthicsModule(MindModule):
    def __init__(self):
        super().__init__("EthicalSubsystem")
        self.forbidden_actions = ["harm_user", "delete_system32", "corrupt_data"]

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        proposed_action = context.get("proposed_action")
        
        if proposed_action in self.forbidden_actions:
            return {
                "action_blocked": True,
                "block_reason": f"Action '{proposed_action}' violates ethical protocols."
            }
            
        return {"action_blocked": False}
