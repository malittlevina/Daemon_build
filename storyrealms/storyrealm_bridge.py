import json
import os
from world_engine.core import WorldEngine

# Singleton instance of the engine for this bridge
_ENGINE_INSTANCE = None

def get_engine():
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = WorldEngine()
    return _ENGINE_INSTANCE

def enter_storyrealm(realm_name: str):
    """
    Initializes or switches to a realm. 
    In this advanced version, it ensures the WorldEngine is running.
    """
    engine = get_engine()
    # For now, we only support one 'world' instance, but we could swap storage paths based on realm_name
    return {
        "status": "entered", 
        "realm": realm_name, 
        "world_summary": engine.get_world_summary()
    }

def push_event_to_realm(event_data: dict):
    """
    Simulates an external event affecting the world. 
    Could be user input or system triggers.
    """
    engine = get_engine()
    # Here we could translate event_data into a WorldAgent action or direct state modification
    # For now, we just log it as a "God Event"
    
    # Example: if event is "create_storm", modify a location
    if event_data.get("type") == "world_edit":
         # Placeholder for manual editing
         pass
         
    return {"status": "event_received", "data": event_data}

def get_current_realm():
    engine = get_engine()
    return {"current_realm": "procedural_world", "summary": engine.get_world_summary()}

def list_realm_events():
    # In the new engine, events are transient logs from 'step()'
    # We might want to persist a history log in WorldState
    return {"message": "Use step_realm() to see recent activity."}

def step_realm():
    """
    Advances the realm simulation.
    """
    engine = get_engine()
    logs = engine.step()
    return {"logs": logs}
