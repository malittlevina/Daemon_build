import asyncio
import json
import random
import time
import websockets

async def mock_engine_client():
    uri = "ws://localhost:8765"
    print(f"[MockEngine] Connecting to Daemon at {uri}...")
    
    async with websockets.connect(uri) as websocket:
        # 1. Handshake
        await websocket.send(json.dumps({
            "type": "handshake", 
            "payload": {"engine_name": "MockUnityv1"}
        }))
        
        # 2. Simulation Loop
        for i in range(10):
            # Create a mock entity moving in a circle
            x = 10 * math.cos(time.time())
            z = 10 * math.sin(time.time())
            
            update_msg = {
                "type": "world_update",
                "payload": {
                    "entities": [
                        {
                            "id": "external_hero_01",
                            "type": "PlayerCharacter",
                            "name": "Hero",
                            "pos": [x, 0, z],
                            "props": {"health": 100}
                        },
                        {
                            "id": "npc_guard_02",
                            "type": "Bot",
                            "name": "Guard",
                            "pos": [5, 0, 5]
                        }
                    ],
                    "global": {"time": time.time()}
                }
            }
            
            await websocket.send(json.dumps(update_msg))
            print(f"[MockEngine] Sent update frame {i}")
            
            # Listen for commands (non-blocking in real app, simplified here)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                print(f"[MockEngine] Received Command: {response}")
            except asyncio.TimeoutError:
                pass
                
            await asyncio.sleep(1)

import math
if __name__ == "__main__":
    try:
        asyncio.run(mock_engine_client())
    except KeyboardInterrupt:
        print("Stopping client.")
