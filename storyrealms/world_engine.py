# storyrealms/world_engine.py
"""
Story Realms World Engine - Core Architecture

The World Engine is the central orchestrator for all Story Realms operations.
It manages world state, entities, narratives, rules, and procedural generation.
Designed as an AI-native symbolic system for intelligent agent management.
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class WorldEngineState(Enum):
    DORMANT = "dormant"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    SIMULATING = "simulating"


@dataclass
class WorldConfig:
    """Configuration for a Story Realm world instance."""
    name: str
    seed: int = 42
    time_scale: float = 1.0  # How fast time passes in-world
    max_entities: int = 10000
    persistence_path: str = "storyrealms/worlds"
    enable_procedural: bool = True
    enable_narrative: bool = True
    rules_module: str = "default"


class WorldEngine:
    """
    The Story Realms World Engine - AI-native world simulation core.
    
    Responsibilities:
    - World state management and persistence
    - Entity lifecycle (spawn, update, despawn)
    - Narrative orchestration (story arcs, quests, dialog)
    - Rule enforcement (world laws, physics, magic)
    - Procedural generation triggers
    - Event propagation and handling
    - Integration with Daemon subsystems
    """
    
    def __init__(self, config: Optional[WorldConfig] = None):
        self.config = config or WorldConfig(name="default_realm")
        self.state = WorldEngineState.DORMANT
        self.world_time = 0.0
        self.tick_count = 0
        
        # Core subsystem references (lazy-loaded)
        self._entity_manager = None
        self._narrative_engine = None
        self._world_rules = None
        self._state_manager = None
        self._procedural_gen = None
        
        # Event queue for cross-system communication
        self.event_queue: List[Dict] = []
        self.event_listeners: Dict[str, List[callable]] = {}
        
        # World metadata
        self.metadata = {
            "created_at": time.time(),
            "last_tick": None,
            "version": "1.0.0",
            "realm_name": self.config.name
        }
        
        print(f"[WorldEngine] Initialized for realm: {self.config.name}")
    
    # ─────────────────────────────────────────────────────────────────
    # LIFECYCLE METHODS
    # ─────────────────────────────────────────────────────────────────
    
    def initialize(self) -> bool:
        """Initialize all world subsystems."""
        self.state = WorldEngineState.INITIALIZING
        print(f"[WorldEngine] Initializing realm '{self.config.name}'...")
        
        try:
            # Initialize subsystems
            self._init_entity_manager()
            self._init_narrative_engine()
            self._init_world_rules()
            self._init_state_manager()
            
            if self.config.enable_procedural:
                self._init_procedural_gen()
            
            self.state = WorldEngineState.ACTIVE
            self._emit_event("world_initialized", {"realm": self.config.name})
            print(f"[WorldEngine] Realm '{self.config.name}' is now ACTIVE")
            return True
            
        except Exception as e:
            print(f"[WorldEngine] Initialization failed: {e}")
            self.state = WorldEngineState.DORMANT
            return False
    
    def shutdown(self):
        """Gracefully shutdown the world engine."""
        print(f"[WorldEngine] Shutting down realm '{self.config.name}'...")
        self._emit_event("world_shutdown", {"realm": self.config.name})
        
        # Persist state before shutdown
        if self._state_manager:
            self._state_manager.save_world_state(self.get_full_state())
        
        self.state = WorldEngineState.DORMANT
        print(f"[WorldEngine] Realm '{self.config.name}' is now DORMANT")
    
    def pause(self):
        """Pause world simulation."""
        if self.state == WorldEngineState.ACTIVE:
            self.state = WorldEngineState.PAUSED
            self._emit_event("world_paused", {})
            print("[WorldEngine] World paused")
    
    def resume(self):
        """Resume world simulation."""
        if self.state == WorldEngineState.PAUSED:
            self.state = WorldEngineState.ACTIVE
            self._emit_event("world_resumed", {})
            print("[WorldEngine] World resumed")
    
    # ─────────────────────────────────────────────────────────────────
    # SIMULATION LOOP
    # ─────────────────────────────────────────────────────────────────
    
    def tick(self, delta_time: float = 1.0) -> Dict:
        """
        Execute one simulation tick.
        
        Args:
            delta_time: Time elapsed since last tick (in world-seconds)
            
        Returns:
            Dict containing tick results and any triggered events
        """
        if self.state != WorldEngineState.ACTIVE:
            return {"status": "skipped", "reason": f"World is {self.state.value}"}
        
        self.state = WorldEngineState.SIMULATING
        tick_results = {
            "tick": self.tick_count,
            "world_time": self.world_time,
            "events": [],
            "entities_updated": 0,
            "narratives_progressed": 0
        }
        
        try:
            # Scale time according to config
            scaled_delta = delta_time * self.config.time_scale
            self.world_time += scaled_delta
            
            # Process pending events
            self._process_event_queue()
            
            # Update entities
            if self._entity_manager:
                entity_results = self._entity_manager.update_all(scaled_delta)
                tick_results["entities_updated"] = entity_results.get("updated", 0)
            
            # Progress narratives
            if self._narrative_engine and self.config.enable_narrative:
                narrative_results = self._narrative_engine.progress_narratives(scaled_delta)
                tick_results["narratives_progressed"] = narrative_results.get("progressed", 0)
            
            # Apply world rules
            if self._world_rules:
                self._world_rules.enforce_all()
            
            # Procedural generation checks
            if self._procedural_gen and self.config.enable_procedural:
                self._procedural_gen.check_generation_triggers()
            
            self.tick_count += 1
            self.metadata["last_tick"] = time.time()
            tick_results["status"] = "success"
            
        except Exception as e:
            tick_results["status"] = "error"
            tick_results["error"] = str(e)
            print(f"[WorldEngine] Tick error: {e}")
        
        self.state = WorldEngineState.ACTIVE
        return tick_results
    
    # ─────────────────────────────────────────────────────────────────
    # EVENT SYSTEM
    # ─────────────────────────────────────────────────────────────────
    
    def _emit_event(self, event_type: str, data: Dict):
        """Emit an event to all registered listeners."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
            "world_time": self.world_time
        }
        self.event_queue.append(event)
        
        # Immediate notification to listeners
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    listener(event)
                except Exception as e:
                    print(f"[WorldEngine] Event listener error: {e}")
    
    def register_listener(self, event_type: str, callback: callable):
        """Register a callback for a specific event type."""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(callback)
    
    def _process_event_queue(self):
        """Process and clear the event queue."""
        processed_events = []
        while self.event_queue:
            event = self.event_queue.pop(0)
            processed_events.append(event)
            # Future: Log events to memory tree
        return processed_events
    
    # ─────────────────────────────────────────────────────────────────
    # SUBSYSTEM INITIALIZATION
    # ─────────────────────────────────────────────────────────────────
    
    def _init_entity_manager(self):
        """Initialize the entity management subsystem."""
        from storyrealms.entity_system import EntityManager
        self._entity_manager = EntityManager(self)
        print("[WorldEngine] Entity Manager initialized")
    
    def _init_narrative_engine(self):
        """Initialize the narrative engine subsystem."""
        from storyrealms.narrative_engine import NarrativeEngine
        self._narrative_engine = NarrativeEngine(self)
        print("[WorldEngine] Narrative Engine initialized")
    
    def _init_world_rules(self):
        """Initialize the world rules subsystem."""
        from storyrealms.world_rules import WorldRules
        self._world_rules = WorldRules(self, self.config.rules_module)
        print("[WorldEngine] World Rules initialized")
    
    def _init_state_manager(self):
        """Initialize the world state persistence manager."""
        from storyrealms.world_state import WorldStateManager
        self._state_manager = WorldStateManager(self.config.persistence_path)
        print("[WorldEngine] State Manager initialized")
    
    def _init_procedural_gen(self):
        """Initialize the procedural generation subsystem."""
        from storyrealms.procedural_gen import ProceduralGenerator
        self._procedural_gen = ProceduralGenerator(self, seed=self.config.seed)
        print("[WorldEngine] Procedural Generator initialized")
    
    # ─────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────
    
    def get_full_state(self) -> Dict:
        """Get the complete world state for persistence or inspection."""
        return {
            "config": asdict(self.config),
            "metadata": self.metadata,
            "world_time": self.world_time,
            "tick_count": self.tick_count,
            "state": self.state.value,
            "entities": self._entity_manager.export_all() if self._entity_manager else [],
            "narratives": self._narrative_engine.export_all() if self._narrative_engine else [],
            "rules": self._world_rules.export_rules() if self._world_rules else {}
        }
    
    def load_state(self, state_data: Dict) -> bool:
        """Load a previously saved world state."""
        try:
            self.world_time = state_data.get("world_time", 0.0)
            self.tick_count = state_data.get("tick_count", 0)
            self.metadata.update(state_data.get("metadata", {}))
            
            if self._entity_manager and "entities" in state_data:
                self._entity_manager.import_all(state_data["entities"])
            
            if self._narrative_engine and "narratives" in state_data:
                self._narrative_engine.import_all(state_data["narratives"])
            
            print(f"[WorldEngine] State loaded successfully")
            return True
        except Exception as e:
            print(f"[WorldEngine] Failed to load state: {e}")
            return False
    
    @property
    def entity_manager(self):
        """Access the entity manager subsystem."""
        return self._entity_manager
    
    @property
    def narrative_engine(self):
        """Access the narrative engine subsystem."""
        return self._narrative_engine
    
    @property
    def world_rules(self):
        """Access the world rules subsystem."""
        return self._world_rules
    
    @property
    def procedural_gen(self):
        """Access the procedural generator subsystem."""
        return self._procedural_gen
    
    # ─────────────────────────────────────────────────────────────────
    # DAEMON INTEGRATION HOOKS
    # ─────────────────────────────────────────────────────────────────
    
    def connect_to_daemon(self, daemon_bridge):
        """Connect the World Engine to the Daemon's bridge system."""
        self.daemon_bridge = daemon_bridge
        self.register_listener("world_event", self._forward_to_daemon)
        print("[WorldEngine] Connected to Daemon bridge")
    
    def _forward_to_daemon(self, event: Dict):
        """Forward world events to the Daemon for processing."""
        if hasattr(self, 'daemon_bridge') and self.daemon_bridge:
            self.daemon_bridge.receive_world_event(event)
    
    def receive_daemon_command(self, command: str, payload: Dict = None) -> Dict:
        """
        Receive and process commands from the Daemon.
        
        Supported commands:
        - spawn_entity: Create a new entity
        - trigger_narrative: Start a narrative arc
        - modify_rules: Update world rules
        - query_state: Get world state information
        """
        payload = payload or {}
        
        command_handlers = {
            "spawn_entity": self._handle_spawn_entity,
            "trigger_narrative": self._handle_trigger_narrative,
            "modify_rules": self._handle_modify_rules,
            "query_state": self._handle_query_state,
            "advance_time": self._handle_advance_time
        }
        
        handler = command_handlers.get(command)
        if handler:
            return handler(payload)
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    
    def _handle_spawn_entity(self, payload: Dict) -> Dict:
        if self._entity_manager:
            entity = self._entity_manager.spawn(**payload)
            return {"status": "success", "entity_id": entity.id if entity else None}
        return {"status": "error", "message": "Entity manager not initialized"}
    
    def _handle_trigger_narrative(self, payload: Dict) -> Dict:
        if self._narrative_engine:
            result = self._narrative_engine.trigger_arc(**payload)
            return {"status": "success", "narrative": result}
        return {"status": "error", "message": "Narrative engine not initialized"}
    
    def _handle_modify_rules(self, payload: Dict) -> Dict:
        if self._world_rules:
            self._world_rules.update_rules(payload)
            return {"status": "success"}
        return {"status": "error", "message": "World rules not initialized"}
    
    def _handle_query_state(self, payload: Dict) -> Dict:
        query_type = payload.get("type", "full")
        if query_type == "full":
            return {"status": "success", "state": self.get_full_state()}
        elif query_type == "entities":
            entities = self._entity_manager.query(**payload) if self._entity_manager else []
            return {"status": "success", "entities": entities}
        elif query_type == "narratives":
            narratives = self._narrative_engine.get_active() if self._narrative_engine else []
            return {"status": "success", "narratives": narratives}
        return {"status": "error", "message": f"Unknown query type: {query_type}"}
    
    def _handle_advance_time(self, payload: Dict) -> Dict:
        delta = payload.get("delta", 1.0)
        result = self.tick(delta)
        return {"status": "success", "tick_result": result}
