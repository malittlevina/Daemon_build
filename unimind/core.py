from typing import Dict, Any, List
from core.events import EventBus, Event
from .modules.base import MindModule
from .modules.logic import LogicModule
from .modules.ethics import EthicsModule
from .modules.strategy import StrategyModule

class Unimind:
    def __init__(self):
        self.bus = None
        self.pipeline: List[MindModule] = []
        
        # Initialize default unified stack
        self._init_modules()
        
        print("[Unimind] Unified Core initialized.")

    def _init_modules(self):
        self.register_module(LogicModule())
        self.register_module(EthicsModule())
        self.register_module(StrategyModule())

    def register_module(self, module: MindModule):
        self.pipeline.append(module)
        print(f"[Unimind] Attached module: {module.name}")

    def register_events(self, bus: EventBus):
        self.bus = bus
        # Listen for analysis requests or game events
        bus.subscribe("unimind:analyze", self._on_analyze_request)
        bus.subscribe("game:encounter", self._on_game_encounter)
        print("[Unimind] Connected to Event Bus.")

    def _on_analyze_request(self, event: Event):
        context = event.payload
        result = self.think(context)
        print(f"[Unimind] Analysis Result: {result}")
        # Optionally publish result back
        if self.bus:
            self.bus.publish("unimind:analysis_complete", result)

    def _on_game_encounter(self, event: Event):
        # Create a thinking context for this encounter
        context = {
            "event_type": "encounter",
            "threat_level": 0.8, # Simulated high threat for enemy
            "entity": event.payload.get("entity")
        }
        print(f"[Unimind] Processing encounter via pipeline...")
        result = self.think(context)
        
        action = result.get("recommended_action")
        print(f"[Unimind] Strategic Recommendation: {action}")

    def think(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Passes the context through the module pipeline.
        Each module can read and modify the context.
        """
        context = initial_context.copy()
        
        for module in self.pipeline:
            updates = module.process(context)
            if updates:
                context.update(updates)
                
            # Early exit if blocked
            if context.get("action_blocked"):
                print(f"[Unimind] Processing halted by {module.name}: {context.get('block_reason')}")
                break
                
        return context

    # Legacy support
    def register(self, type, module):
        # We don't use the old list dict anymore but keep for compatibility if main calls it
        pass
    
    def reflect(self):
        # Simple self-check
        pass
