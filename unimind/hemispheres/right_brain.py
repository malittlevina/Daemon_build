from typing import Dict, Any, List
from ..modules.base import MindModule
from ..modules.creative import CreativeModule

class RightHemisphere:
    def __init__(self):
        self.modules: List[MindModule] = [
            CreativeModule()
        ]

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("[RightBrain] Seeking patterns and inspiration...")
        hemisphere_context = context.copy()
        updates = {}
        
        for module in self.modules:
            mod_updates = module.process(hemisphere_context)
            if mod_updates:
                hemisphere_context.update(mod_updates)
                updates.update(mod_updates)
                
        return updates
