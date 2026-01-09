# storyrealms/storyrealm_bridge.py
"""
Story Realms Bridge - Main interface for the World Engine

This bridge connects the Story Realms World Engine to the Daemon's
subsystems (scrolls, memory tree, NLU, etc.) and provides a unified
API for realm management.
"""

import json
import os
from typing import Dict, List, Optional, Any

# Import World Engine components
from storyrealms.world_engine import WorldEngine, WorldConfig, WorldEngineState


class StoryRealmsBridge:
    """
    Bridge connecting Story Realms World Engine to the Daemon.
    
    Provides:
    - Realm lifecycle management
    - Daemon subsystem integration
    - Event routing between systems
    - Command dispatch to World Engine
    """
    
    _instance = None
    _active_engines: Dict[str, WorldEngine] = {}
    _current_realm: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._daemon_bridge = None
        self._memory_interface = None
        self._scroll_engine = None
        
        print("[StoryRealmsBridge] Initialized")
    
    # ─────────────────────────────────────────────────────────────────
    # REALM LIFECYCLE
    # ─────────────────────────────────────────────────────────────────
    
    def create_realm(self, name: str, config: Dict = None) -> Dict:
        """Create a new Story Realm."""
        if name in self._active_engines:
            return {"status": "error", "message": f"Realm '{name}' already exists"}
        
        # Build configuration
        world_config = WorldConfig(
            name=name,
            seed=config.get("seed", 42) if config else 42,
            time_scale=config.get("time_scale", 1.0) if config else 1.0,
            enable_procedural=config.get("procedural", True) if config else True,
            enable_narrative=config.get("narrative", True) if config else True,
            rules_module=config.get("rules", "default") if config else "default"
        )
        
        # Create and initialize engine
        engine = WorldEngine(world_config)
        engine.initialize()
        
        # Connect to daemon if available
        if self._daemon_bridge:
            engine.connect_to_daemon(self)
        
        # Register event listeners for memory logging
        engine.register_listener("entity_spawned", self._on_entity_spawned)
        engine.register_listener("narrative_triggered", self._on_narrative_triggered)
        engine.register_listener("narrative_completed", self._on_narrative_completed)
        
        self._active_engines[name] = engine
        
        print(f"[StoryRealmsBridge] Created realm: {name}")
        return {
            "status": "created",
            "realm": name,
            "state": engine.state.value
        }
    
    def enter_realm(self, name: str) -> Dict:
        """Enter an existing realm (make it current)."""
        if name not in self._active_engines:
            # Try to load from persistence
            loaded = self._load_realm(name)
            if not loaded:
                return {"status": "error", "message": f"Realm '{name}' not found"}
        
        self._current_realm = name
        engine = self._active_engines[name]
        
        # Resume if paused
        if engine.state == WorldEngineState.PAUSED:
            engine.resume()
        
        print(f"[StoryRealmsBridge] Entered realm: {name}")
        return {
            "status": "entered",
            "realm": name,
            "world_time": engine.world_time,
            "entity_count": len(engine.entity_manager.entities) if engine.entity_manager else 0
        }
    
    def exit_realm(self) -> Dict:
        """Exit the current realm (pause it)."""
        if not self._current_realm:
            return {"status": "error", "message": "No realm currently active"}
        
        engine = self._active_engines.get(self._current_realm)
        if engine:
            engine.pause()
        
        realm = self._current_realm
        self._current_realm = None
        
        print(f"[StoryRealmsBridge] Exited realm: {realm}")
        return {"status": "exited", "realm": realm}
    
    def destroy_realm(self, name: str) -> Dict:
        """Destroy a realm and clean up resources."""
        if name not in self._active_engines:
            return {"status": "error", "message": f"Realm '{name}' not found"}
        
        engine = self._active_engines.pop(name)
        engine.shutdown()
        
        if self._current_realm == name:
            self._current_realm = None
        
        print(f"[StoryRealmsBridge] Destroyed realm: {name}")
        return {"status": "destroyed", "realm": name}
    
    def _load_realm(self, name: str) -> bool:
        """Attempt to load a realm from persistence."""
        from storyrealms.world_state import WorldStateManager
        
        state_manager = WorldStateManager()
        state_data = state_manager.load_world_state(name)
        
        if not state_data:
            return False
        
        # Create engine and load state
        config_data = state_data.get("config", {})
        world_config = WorldConfig(
            name=name,
            seed=config_data.get("seed", 42),
            time_scale=config_data.get("time_scale", 1.0)
        )
        
        engine = WorldEngine(world_config)
        engine.initialize()
        engine.load_state(state_data)
        
        self._active_engines[name] = engine
        return True
    
    # ─────────────────────────────────────────────────────────────────
    # REALM INTERACTION
    # ─────────────────────────────────────────────────────────────────
    
    def get_current_engine(self) -> Optional[WorldEngine]:
        """Get the currently active World Engine."""
        if self._current_realm:
            return self._active_engines.get(self._current_realm)
        return None
    
    def tick(self, delta_time: float = 1.0) -> Dict:
        """Advance the current realm by one tick."""
        engine = self.get_current_engine()
        if not engine:
            return {"status": "error", "message": "No active realm"}
        
        return engine.tick(delta_time)
    
    def send_command(self, command: str, payload: Dict = None) -> Dict:
        """Send a command to the current realm's World Engine."""
        engine = self.get_current_engine()
        if not engine:
            return {"status": "error", "message": "No active realm"}
        
        return engine.receive_daemon_command(command, payload)
    
    def query_state(self, query_type: str = "full", **params) -> Dict:
        """Query the current realm's state."""
        engine = self.get_current_engine()
        if not engine:
            return {"status": "error", "message": "No active realm"}
        
        return engine.receive_daemon_command("query_state", {"type": query_type, **params})
    
    # ─────────────────────────────────────────────────────────────────
    # DAEMON INTEGRATION
    # ─────────────────────────────────────────────────────────────────
    
    def connect_daemon_bridge(self, bridge):
        """Connect to the Daemon's ThothBridge."""
        self._daemon_bridge = bridge
        print("[StoryRealmsBridge] Connected to Daemon bridge")
    
    def connect_memory_interface(self, memory_interface):
        """Connect to the Daemon's Memory Tree."""
        self._memory_interface = memory_interface
        print("[StoryRealmsBridge] Connected to Memory Tree")
    
    def connect_scroll_engine(self, scroll_engine):
        """Connect to the Daemon's Scroll Engine."""
        self._scroll_engine = scroll_engine
        print("[StoryRealmsBridge] Connected to Scroll Engine")
    
    def receive_world_event(self, event: Dict):
        """Receive events from the World Engine for daemon processing."""
        event_type = event.get("type", "unknown")
        
        # Log to memory tree
        if self._memory_interface:
            self._memory_interface.plant_memory_seed(
                content=f"World event: {event_type} - {event.get('data', {})}",
                tags=["world_event", event_type],
                context="storyrealms"
            )
        
        # Check for scroll triggers
        if self._scroll_engine:
            self._check_scroll_triggers(event)
    
    def _check_scroll_triggers(self, event: Dict):
        """Check if any scrolls should be triggered by this event."""
        # Future: Integrate with scroll trigger system
        pass
    
    # ─────────────────────────────────────────────────────────────────
    # EVENT HANDLERS
    # ─────────────────────────────────────────────────────────────────
    
    def _on_entity_spawned(self, event: Dict):
        """Handle entity spawn events."""
        if self._memory_interface:
            data = event.get("data", {})
            self._memory_interface.plant_memory_seed(
                content=f"Entity spawned: {data.get('name', 'Unknown')} ({data.get('type', 'unknown')})",
                tags=["entity", "spawn", data.get("type", "unknown")],
                context="storyrealms"
            )
    
    def _on_narrative_triggered(self, event: Dict):
        """Handle narrative trigger events."""
        if self._memory_interface:
            data = event.get("data", {})
            self._memory_interface.plant_memory_seed(
                content=f"Narrative started: {data.get('title', 'Unknown')}",
                tags=["narrative", "started", data.get("type", "unknown")],
                context="storyrealms"
            )
    
    def _on_narrative_completed(self, event: Dict):
        """Handle narrative completion events."""
        if self._memory_interface:
            data = event.get("data", {})
            self._memory_interface.plant_memory_seed(
                content=f"Narrative completed: {data.get('title', 'Unknown')} ({data.get('reason', 'unknown')})",
                tags=["narrative", "completed"],
                context="storyrealms"
            )
    
    # ─────────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────────
    
    def list_realms(self) -> Dict:
        """List all active realms."""
        realms = []
        for name, engine in self._active_engines.items():
            realms.append({
                "name": name,
                "state": engine.state.value,
                "world_time": engine.world_time,
                "is_current": name == self._current_realm
            })
        return {"realms": realms, "current": self._current_realm}
    
    def get_realm_info(self, name: str = None) -> Dict:
        """Get detailed information about a realm."""
        name = name or self._current_realm
        if not name or name not in self._active_engines:
            return {"status": "error", "message": "Realm not found"}
        
        engine = self._active_engines[name]
        return {
            "name": name,
            "state": engine.state.value,
            "world_time": engine.world_time,
            "tick_count": engine.tick_count,
            "metadata": engine.metadata,
            "entity_count": len(engine.entity_manager.entities) if engine.entity_manager else 0,
            "active_narratives": len(engine.narrative_engine.active_narratives) if engine.narrative_engine else 0
        }


# ─────────────────────────────────────────────────────────────────────
# LEGACY API COMPATIBILITY
# These functions maintain backward compatibility with the old API
# ─────────────────────────────────────────────────────────────────────

_bridge = None

def _get_bridge() -> StoryRealmsBridge:
    """Get or create the singleton bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = StoryRealmsBridge()
    return _bridge

def enter_storyrealm(realm_name: str) -> Dict:
    """Legacy API: Enter a story realm."""
    bridge = _get_bridge()
    
    # Create if doesn't exist
    if realm_name not in bridge._active_engines:
        bridge.create_realm(realm_name)
    
    return bridge.enter_realm(realm_name)

def push_event_to_realm(event_data: dict) -> Dict:
    """Legacy API: Push an event to the current realm."""
    bridge = _get_bridge()
    engine = bridge.get_current_engine()
    
    if not engine:
        return {"status": "error", "message": "No active realm"}
    
    engine._emit_event(event_data.get("type", "custom"), event_data)
    return {"status": "event_pushed", "event": event_data}

def get_current_realm() -> Dict:
    """Legacy API: Get the current realm."""
    bridge = _get_bridge()
    return {"current_realm": bridge._current_realm}

def list_realm_events() -> Dict:
    """Legacy API: List events from the current realm."""
    bridge = _get_bridge()
    engine = bridge.get_current_engine()
    
    if not engine:
        return {"events": []}
    
    return {"events": engine.event_queue}
