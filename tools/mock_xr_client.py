import asyncio
import json
import random
import time
import websockets

async def mock_xr_client():
    uri = "ws://localhost:8765"
    print(f"[MockXR] Connecting to Daemon at {uri}...")
    
    async with websockets.connect(uri) as websocket:
        # 1. Handshake
        await websocket.send(json.dumps({
            "type": "handshake", 
            "payload": {"engine_name": "MockQuest3"}
        }))
        
        objects = ["cat", "laptop", "coffee_mug", "window"]
        
        # 2. Simulation Loop
        for i in range(20):
            # Simulate looking left/right
            # x ranges from -1 (left) to 1 (right)
            gaze_x = math.sin(time.time()) 
            
            # Simulate object recognition
            obj = objects[i % 4]
            
            update_msg = {
                "type": "xr_update",
                "payload": {
                    "gaze_vector": [gaze_x, 0, 1],
                    "looked_at_object": obj,
                    "confidence": 0.98
                }
            }
            
            await websocket.send(json.dumps(update_msg))
            print(f"[MockXR] Gaze X: {gaze_x:.2f} | Looking at: {obj}")
            
            await asyncio.sleep(1)

import math
if __name__ == "__main__":
    try:
        asyncio.run(mock_xr_client())
    except KeyboardInterrupt:
        print("Stopping client.")
