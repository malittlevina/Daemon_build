# interface/neural_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading
import uvicorn
import json

# Import daemon internals (using global instances where possible or dependency injection)
from emotion.emotion_engine import emotion_state
from memory_tree.memory_logger import retrieve_log, log_memory
from daemon.kernel_bridge import KernelBridge
from storyrealms.engine import StoryRealmsEngine

app = FastAPI(title="Daemon Neural Interface", version="1.0.0")

# --- Models ---
class InputPayload(BaseModel):
    text: str
    source: str = "api"
    client_id: str = "guest"  # New field for multiplayer identification

class JoinPayload(BaseModel):
    client_id: str
    player_name: str
    realm_name: str

# ... (existing imports)

@app.post("/join")
def join_realm(payload: JoinPayload):
    world = get_world()
    
    # Switch global context (Shared World Model)
    # Note: In a true multi-realm server, we wouldn't switch the *global* current_realm,
    # but rather handle players in specific instances. For now, we assume one active realm.
    if world.current_realm and world.current_realm.name != payload.realm_name:
        if not world.enter_realm(payload.realm_name):
            return {"error": "Realm not found"}
            
    player = world.current_realm.add_player(payload.client_id, payload.player_name)
    world.save_realm(world.current_realm)
    
    return {
        "status": "joined",
        "realm": payload.realm_name,
        "location": player.location,
        "message": f"Welcome to {payload.realm_name}, {payload.player_name}."
    }

@app.post("/interact")
def interact(payload: InputPayload):
    world = get_world()
    if not world.current_realm:
        return {"error": "No active realm"}

    # Handle multiplayer actions
    player = world.current_realm.active_players.get(payload.client_id)
    
    response_text = ""
    
    if player:
        # Simple parser for player actions
        text = payload.text.lower()
        if text.startswith("move "):
            dest = text.replace("move ", "").strip()
            if player.move(dest, {"current_realm": world.current_realm}):
                response_text = f"Moved to {dest}"
            else:
                response_text = f"Cannot move to {dest}"
@app.post("/interact")
def interact(payload: InputPayload):
    world = get_world()
    if not world.current_realm:
        return {"error": "No active realm"}

    # Handle multiplayer actions
    player = world.current_realm.active_players.get(payload.client_id)
    
    response_text = ""
    
    if player:
        # Simple parser for player actions
        text = payload.text.lower()
        if text.startswith("move "):
            dest = text.replace("move ", "").strip()
            if player.move(dest, {"current_realm": world.current_realm}):
                response_text = f"Moved to {dest}"
            else:
                response_text = f"Cannot move to {dest}"
        elif text.startswith("interact "):
            target = text.replace("interact ", "").strip()
            response_text = player.interact(target, {"current_realm": world.current_realm})
        elif text.startswith("attack "):
            # Sentry Integration
            target = text.replace("attack ", "").strip()
            from guardian.sentry import CyberSentry
            sentry = CyberSentry(world)
            response_text = sentry.exorcise_entity(target, world.current_realm.name)
        else:
            response_text = f"Logged: {payload.text}"
            log_memory(f"Player {player.name}: {payload.text}", {"realm": world.current_realm.name})
            
        # Save state
        world.save_realm(world.current_realm)
    else:
        # Guest / System interaction
        log_memory(f"API Input Received: {payload.text}", {"source": payload.source})
        response_text = "Input received (Guest Mode)."

    emotion_state.update_emotion("interaction")
    return {"response": response_text, "context": world.get_current_context()}

# --- Runner ---
def start_api_server(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_api_server()
