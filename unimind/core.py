import traceback
from typing import Dict, Any, List, Optional
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
        
        print("[Unimind] Bicameral Mind initialized with robust error handling.")

    def register_events(self, bus: EventBus):
        self.bus = bus
        bus.subscribe("unimind:analyze", self._on_analyze_request)
        bus.subscribe("game:encounter", self._on_game_encounter)
        print("[Unimind] Connected to Event Bus.")

    def _on_analyze_request(self, event: Event):
        try:
            context = event.payload
            result = self.think(context)
            print(f"[Unimind] Analysis Result: {result}")
            if self.bus:
                self.bus.publish("unimind:analysis_complete", result)
        except Exception as e:
            print(f"[Unimind Error] Failed to process analysis request: {e}")
            self._send_error_response("analysis_failed", str(e))

    def _on_game_encounter(self, event: Event):
        try:
            context = {
                "event_type": "encounter",
                "threat_level": 0.8, 
                "entity": event.payload.get("entity")
            }
            print(f"[Unimind] Processing encounter...")
            result = self.think(context)
            
            action = result.get("selected_option", result.get("recommended_action", "observe"))
            print(f"[Unimind] Final Decision: {action}")
            
            if self.bus:
                self.bus.publish("unimind:decision", {"decision": action, "context": result})
        except Exception as e:
            print(f"[Unimind Error] Encounter processing failed: {e}")
            # Fallback safe action
            if self.bus:
                self.bus.publish("unimind:decision", {"decision": "defend", "reason": "system_error_fallback"})

    def _send_error_response(self, error_type: str, message: str):
        if self.bus:
            self.bus.publish("unimind:error", {"type": error_type, "message": message})

    def think(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bicameral Processing with Safety Nets:
        1. Input Validation
        2. Isolated Hemisphere Execution (Try/Except)
        3. Conflict Resolution
        4. Safe Fallback
        """
        # 0. Safety & Validation
        if not isinstance(initial_context, dict):
            print("[Unimind Warning] Invalid context type. Creating empty context.")
            context = {}
        else:
            context = initial_context.copy()

        try:
            # 1. Left Brain Processing (Logic/Safety)
            try:
                left_updates = self.left_brain.process(context)
                context.update(left_updates)
            except Exception as e:
                print(f"[Unimind] Left Brain Logic Failure: {e}")
                traceback.print_exc()
                # If logic fails, assume maximum safety
                context["defensive_posture"] = True
                context["action_blocked"] = False # Don't block, but proceed with caution

            # 2. Right Brain Processing (Creative)
            try:
                right_updates = self.right_brain.process(context)
                context.update(right_updates)
            except Exception as e:
                print(f"[Unimind] Right Brain Intuition Failure: {e}")
                # If creativity fails, we just lose the creative options, proceed with logic
            
            # Conflict Resolution / Synthesis
            if context.get("action_blocked"):
                print(f"[Unimind] Left Brain Halt: {context.get('block_reason')}")
                return context
                
            # 3. Synthesis (Strategy)
            try:
                final_updates = self.synthesizer.process(context)
                context.update(final_updates)
            except Exception as e:
                print(f"[Unimind] Synthesizer Failure: {e}")
                # Fallback choice logic if synthesizer breaks
                if "options" in context and context["options"]:
                    # Just pick the first available option safely
                    first_opt = list(context["options"].keys())[0]
                    context["selected_option"] = first_opt
                else:
                    context["selected_option"] = context.get("recommended_action", "wait")
            
            return context

        except Exception as critical_e:
            print(f"[Unimind Critical Failure] Core panic: {critical_e}")
            traceback.print_exc()
            return {
                "error": True, 
                "message": str(critical_e),
                "selected_option": "system_restart_recommended"
            }

    # Legacy support
    def register(self, type, module):
        pass
    
    def reflect(self):
        pass
