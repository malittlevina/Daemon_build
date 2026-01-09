from typing import Dict, Any, List
from ..modules.base import MindModule
from ..modules.logic import LogicModule
from ..modules.ethics import EthicsModule

class LeftHemisphere:
    def __init__(self):
        self.modules: List[MindModule] = [
            LogicModule(),
            EthicsModule()
        ]

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("[LeftBrain] Analyzing structure and safety...")
        hemisphere_context = context.copy()
        updates = {}
        
        for module in self.modules:
            mod_updates = module.process(hemisphere_context)
            if mod_updates:
                hemisphere_context.update(mod_updates)
                updates.update(mod_updates)
            
            # If ethics blocks, we stop early in this hemisphere
            if hemisphere_context.get("action_blocked"):
                break
                
        return updates
