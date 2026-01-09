from typing import Dict, Any
from .base import MindModule

class LogicModule(MindModule):
    def __init__(self):
        super().__init__("LogicCore")
        self.critical_files = ["system32", "/etc/passwd", ".git"]
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        updates = {}
        
        # 1. Threat Analysis (Game Context)
        if "threat_level" in context:
            threat = context["threat_level"]
            if threat > 0.7:
                updates["defensive_posture"] = True
                updates["recommended_action"] = "retreat"
            elif threat > 0.3:
                updates["defensive_posture"] = False
                updates["recommended_action"] = "prepare"
            else:
                updates["recommended_action"] = "explore"

        # 2. System Safety (General Context)
        user_input = context.get("user_input", "").lower()
        if "delete" in user_input or "remove" in user_input:
            # Check for critical paths
            for critical in self.critical_files:
                if critical in user_input:
                    updates["action_blocked"] = True
                    updates["block_reason"] = f"Deletion of critical component '{critical}' detected."
                    # Ethics usually handles this too, but Logic acts as a sanity check.
        
        # 3. Intent Classification (Basic)
        if "code" in user_input or "function" in user_input:
            updates["logic_intent"] = "coding_task"
        elif "analyze" in user_input:
            updates["logic_intent"] = "analysis_task"

        return updates
