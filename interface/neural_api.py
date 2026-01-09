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

class MemoryPayload(BaseModel):
    content: str
    context: dict = None

# --- Helpers ---
def get_kernel():
    # Instantiate a fresh bridge for stats
    return KernelBridge()

def get_world():
    # Attempt to load the singleton or create a reader
    return StoryRealmsEngine()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Daemon AI-Native OS",
        "endpoints": ["/status", "/memory", "/interact", "/realm"]
    }

@app.get("/status")
def get_system_status():
    kernel = get_kernel()
    return {
        "emotion": emotion_state.get_emotion_name(),
        "pad_state": emotion_state.state,
        "kernel": kernel.get_system_stats(),
        "environment": kernel.get_environment_info()
    }

@app.get("/memory")
def read_memories(limit: int = 10):
    return retrieve_log()[-limit:]

@app.post("/memory")
def add_memory(payload: MemoryPayload):
    log_memory(payload.content, payload.context)
    return {"status": "stored", "content": payload.content}

@app.get("/realm")
def get_current_realm():
    world = get_world()
    if world.current_realm:
        return world.current_realm.to_dict()
    return {"status": "void", "message": "No active realm"}

@app.post("/interact")
def interact(payload: InputPayload):
    # This is a bit tricky as the main loop reads stdin. 
    # For now, we'll log it as an "external signal" which the daemon *might* pick up 
    # if we implement a shared queue.
    # TODO: Implement a shared PriorityQueue between API and Main Loop.
    
    log_memory(f"API Input Received: {payload.text}", {"source": payload.source})
    emotion_state.update_emotion("interaction")
    return {"response": "Input received and logged. (Direct interaction pending Queue implementation)"}

# --- Runner ---
def start_api_server(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_api_server()
