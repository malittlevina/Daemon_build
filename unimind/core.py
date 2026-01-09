from typing import Dict, Any, List
from core.events import EventBus, Event
from .modules.strategy import StrategyModule
from .hemispheres.left_brain import LeftHemisphere
from .hemispheres.right_brain import RightHemisphere

class Unimind:
    def __init__(self):
        self.bus = None
        
        # The Two Hemispheres
        self.left_brain = LeftHemisphere()
        self.right_brain = RightHemisphere()
        
        # The Integrator
        self.synthesizer = StrategyModule()
        
        print("[Unimind] Bicameral Mind initialized.")

    def register_events(self, bus: EventBus):
        self.bus = bus
        bus.subscribe("unimind:analyze", self._on_analyze_request)
        bus.subscribe("game:encounter", self._on_game_encounter)
        print("[Unimind] Connected to Event Bus.")

    def _on_analyze_request(self, event: Event):
        context = event.payload
        result = self.think(context)
        print(f"[Unimind] Analysis Result: {result}")
        if self.bus:
            self.bus.publish("unimind:analysis_complete", result)

    def _on_game_encounter(self, event: Event):
        context = {
            "event_type": "encounter",
            "threat_level": 0.8, 
            "entity": event.payload.get("entity")
        }
        print(f"[Unimind] Processing encounter...")
        result = self.think(context)
        
        action = result.get("selected_option", result.get("recommended_action"))
        print(f"[Unimind] Final Decision: {action}")
        
        if self.bus:
            self.bus.publish("unimind:decision", {"decision": action, "context": result})

    def think(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bicameral Processing:
        1. Left Brain analyzes logic/safety.
        2. Right Brain generates creative options.
        3. Synthesizer merges and decides.
        """
        context = initial_context.copy()
        
        # 1. Left Brain Processing
        left_updates = self.left_brain.process(context)
        
        # 2. Right Brain Processing
        right_updates = self.right_brain.process(context)
        
        # Merge (Right brain adds to options, Left brain sets constraints/recommendations)
        # Note: If Left Brain blocks an action, we must respect it.
        context.update(left_updates)
        context.update(right_updates) # Right brain might overwrite or add
        
        # Conflict Resolution / Synthesis
        if context.get("action_blocked"):
            print(f"[Unimind] Left Brain Halt: {context.get('block_reason')}")
            return context
            
        # 3. Synthesis (Strategy)
        final_updates = self.synthesizer.process(context)
        context.update(final_updates)
        
        return context

    # Legacy support
    def register(self, type, module):
        pass
    
    def reflect(self):
        pass
