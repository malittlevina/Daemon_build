# bridge/realm_interface.py
"""
Realm Interface - Bridge between Daemon and Story Realms World Engine

This interface provides the Daemon's primary connection to Story Realms,
enabling command dispatch, event handling, and state queries.
"""

from typing import Dict, List, Optional, Any


class RealmInterface:
    """
    Interface connecting the Daemon to Story Realms World Engine.
    
    Provides:
    - Realm connection management
    - Command dispatch to World Engine
    - Event routing
    - State queries
    """
    
    def __init__(self):
        self.connected = False
        self.current_realm = None
        self._storyrealms_bridge = None
        
        # Attempt to connect to Story Realms
        self._connect_to_storyrealms()
        
        print("[RealmInterface] Initialized.")
    
    def _connect_to_storyrealms(self):
        """Connect to the Story Realms bridge."""
        try:
            from storyrealms.storyrealm_bridge import StoryRealmsBridge
            self._storyrealms_bridge = StoryRealmsBridge()
            print("[RealmInterface] Connected to Story Realms World Engine")
        except ImportError as e:
            print(f"[RealmInterface] Story Realms not available: {e}")
    
    def enter_realm(self, realm_name: str) -> Dict:
        """
        Enter a Story Realm.
        
        Creates the realm if it doesn't exist, then activates it.
        """
        if not self._storyrealms_bridge:
            self._connect_to_storyrealms()
        
        if self._storyrealms_bridge:
            # Create realm if needed
            result = self._storyrealms_bridge.enter_realm(realm_name)
            
            if result.get("status") == "error" and "not found" in result.get("message", ""):
                # Create new realm
                self._storyrealms_bridge.create_realm(realm_name)
                result = self._storyrealms_bridge.enter_realm(realm_name)
            
            if result.get("status") == "entered":
                self.connected = True
                self.current_realm = realm_name
            
            print(f"[RealmInterface] Entering realm: {realm_name}")
            return result
        
        # Fallback for when Story Realms not available
        self.connected = True
        self.current_realm = realm_name
        return {"status": "entered", "realm": realm_name, "mode": "legacy"}
    
    def exit_realm(self) -> Dict:
        """Exit the current realm."""
        if self._storyrealms_bridge:
            result = self._storyrealms_bridge.exit_realm()
            self.connected = False
            self.current_realm = None
            return result
        
        self.connected = False
        self.current_realm = None
        return {"status": "exited"}
    
    def send_command(self, command: str, payload: Dict = None) -> Dict:
        """
        Send a command to the current realm's World Engine.
        
        Supported commands:
        - spawn_entity: Create a new entity
        - trigger_narrative: Start a narrative/quest
        - modify_rules: Update world rules
        - query_state: Get world state
        - advance_time: Tick the simulation
        """
        if not self.connected:
            print("[RealmInterface] No realm connected. Command not sent.")
            return {"status": "error", "message": "Not connected to realm"}
        
        if self._storyrealms_bridge:
            result = self._storyrealms_bridge.send_command(command, payload)
            print(f"[RealmInterface] Command '{command}' sent to realm '{self.current_realm}'")
            return result
        
        # Legacy fallback
        print(f"[RealmInterface] Sending command to realm '{self.current_realm}': {command}")
        return {"status": "sent", "command": command, "mode": "legacy"}
    
    def send_event(self, event_type: str, data: dict) -> Dict:
        """Send an event to the current realm."""
        if not self.connected:
            print("[RealmInterface] No realm connected. Event ignored.")
            return {"status": "error", "message": "Not connected"}
        
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine:
                engine._emit_event(event_type, data)
                return {"status": "emitted", "event_type": event_type}
        
        print(f"[RealmInterface] Event: {event_type} | Data: {data}")
        return {"status": "sent", "event_type": event_type, "mode": "legacy"}
    
    def get_current_state(self) -> Dict:
        """Get the current realm's state."""
        if not self.connected:
            return {
                "realm": None,
                "status": "disconnected"
            }
        
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine:
                return {
                    "realm": self.current_realm,
                    "status": engine.state.value,
                    "world_time": engine.world_time,
                    "tick_count": engine.tick_count,
                    "entity_count": len(engine.entity_manager.entities) if engine.entity_manager else 0,
                    "active_narratives": len(engine.narrative_engine.active_narratives) if engine.narrative_engine else 0
                }
        
        return {
            "realm": self.current_realm,
            "objects": [],
            "status": "stable" if self.connected else "disconnected"
        }
    
    # ─────────────────────────────────────────────────────────────────
    # ENTITY OPERATIONS
    # ─────────────────────────────────────────────────────────────────
    
    def spawn_entity(
        self,
        name: str,
        entity_type: str,
        location_id: str = None,
        attributes: Dict = None,
        **kwargs
    ) -> Dict:
        """Spawn a new entity in the current realm."""
        return self.send_command("spawn_entity", {
            "name": name,
            "entity_type": entity_type,
            "location_id": location_id,
            "attributes": attributes or {},
            **kwargs
        })
    
    def get_entities(self, **filters) -> Dict:
        """Query entities in the current realm."""
        return self.send_command("query_state", {
            "type": "entities",
            **filters
        })
    
    def interact_entities(self, source_id: str, target_id: str, interaction_type: str) -> Dict:
        """Record an interaction between entities."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine and engine.entity_manager:
                return engine.entity_manager.interact(source_id, target_id, interaction_type)
        return {"status": "error", "message": "Entity manager not available"}
    
    # ─────────────────────────────────────────────────────────────────
    # NARRATIVE OPERATIONS
    # ─────────────────────────────────────────────────────────────────
    
    def trigger_narrative(self, title: str, narrative_type: str = "quest", **kwargs) -> Dict:
        """Trigger a new narrative (quest, story arc, etc.)."""
        return self.send_command("trigger_narrative", {
            "title": title,
            "narrative_type": narrative_type,
            **kwargs
        })
    
    def start_dialog(self, speaker_id: str, listener_id: str) -> Dict:
        """Start a dialog between two entities."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine and engine.narrative_engine:
                return engine.narrative_engine.start_dialog(speaker_id, listener_id)
        return {"status": "error", "message": "Narrative engine not available"}
    
    def continue_dialog(self, session_id: str, choice_id: str) -> Dict:
        """Continue a dialog with a choice."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine and engine.narrative_engine:
                return engine.narrative_engine.continue_dialog(session_id, choice_id)
        return {"status": "error", "message": "Narrative engine not available"}
    
    # ─────────────────────────────────────────────────────────────────
    # SIMULATION CONTROL
    # ─────────────────────────────────────────────────────────────────
    
    def tick(self, delta_time: float = 1.0) -> Dict:
        """Advance the world simulation by one tick."""
        return self.send_command("advance_time", {"delta": delta_time})
    
    def pause(self) -> Dict:
        """Pause the current realm's simulation."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine:
                engine.pause()
                return {"status": "paused"}
        return {"status": "error", "message": "No engine available"}
    
    def resume(self) -> Dict:
        """Resume the current realm's simulation."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine:
                engine.resume()
                return {"status": "resumed"}
        return {"status": "error", "message": "No engine available"}
    
    # ─────────────────────────────────────────────────────────────────
    # PROCEDURAL GENERATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_npc(self, **kwargs) -> Dict:
        """Generate a procedural NPC."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine and engine.procedural_gen:
                return engine.procedural_gen.generate_npc(**kwargs)
        return {"status": "error", "message": "Procedural generator not available"}
    
    def generate_location(self, **kwargs) -> Dict:
        """Generate a procedural location."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine and engine.procedural_gen:
                return engine.procedural_gen.generate_location(**kwargs)
        return {"status": "error", "message": "Procedural generator not available"}
    
    def generate_quest(self, **kwargs) -> Dict:
        """Generate a procedural quest."""
        if self._storyrealms_bridge:
            engine = self._storyrealms_bridge.get_current_engine()
            if engine and engine.procedural_gen:
                return engine.procedural_gen.generate_quest(**kwargs)
        return {"status": "error", "message": "Procedural generator not available"}
