import asyncio
import json
import threading
from typing import Dict, Any, Callable

# Simple event definitions
EVENT_CONNECT = "connect"
EVENT_DISCONNECT = "disconnect"
EVENT_STATE_UPDATE = "state_update"
EVENT_ACTION = "action"

class SpatialServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()
        self.loop = None
        self.callbacks = {
            EVENT_CONNECT: [],
            EVENT_DISCONNECT: [],
            EVENT_STATE_UPDATE: [],
            EVENT_ACTION: []
        }
        self.running = False

    def start(self):
        self.running = True
        # Run event loop in a separate thread
        thread = threading.Thread(target=self._run_loop, daemon=True)
        thread.start()
        print(f"[SpatialServer] Listening on ws://{self.host}:{self.port}")

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            import websockets
            start_server = websockets.serve(self._handler, self.host, self.port)
            self.loop.run_until_complete(start_server)
            self.loop.run_forever()
        except ImportError:
            print("[SpatialServer] 'websockets' lib not installed. Server disabled.")
        except Exception as e:
            print(f"[SpatialServer] Error: {e}")

    async def _handler(self, websocket, path):
        self.clients.add(websocket)
        self._trigger(EVENT_CONNECT, {"client_id": id(websocket)})
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    payload = data.get("payload", {})
                    
                    if msg_type == "world_update":
                        self._trigger(EVENT_STATE_UPDATE, payload)
                    elif msg_type == "action_result":
                        self._trigger(EVENT_ACTION, payload)
                    elif msg_type == "handshake":
                        print(f"[SpatialServer] Handshake from: {payload.get('engine_name')}")
                    else:
                        print(f"[SpatialServer] Unknown message type: {msg_type}")
                        
                except json.JSONDecodeError:
                    print(f"[SpatialServer] Invalid JSON received: {message}")
        except Exception as e:
            print(f"[SpatialServer] Connection error: {e}")
        finally:
            self.clients.remove(websocket)
            self._trigger(EVENT_DISCONNECT, {"client_id": id(websocket)})

    def send_command(self, action: str, target_id: str, params: Dict[str, Any] = None):
        """
        Sends a command back to the connected 3D engine.
        """
        if not self.loop or not self.clients:
            return

        message = {
            "type": "ai_command",
            "payload": {
                "action": action,
                "target_id": target_id,
                "params": params or {}
            }
        }
        json_msg = json.dumps(message)
        
        # Schedule the send in the asyncio loop
        asyncio.run_coroutine_threadsafe(self._broadcast(json_msg), self.loop)

    async def _broadcast(self, message):
        import websockets
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    def on(self, event_name: str, callback: Callable):
        if event_name in self.callbacks:
            self.callbacks[event_name].append(callback)

    def _trigger(self, event_name: str, data: Any):
        for cb in self.callbacks[event_name]:
            try:
                cb(data)
            except Exception as e:
                print(f"[SpatialServer] Callback error: {e}")
