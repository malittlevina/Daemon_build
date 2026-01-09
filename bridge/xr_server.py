from core.module import Module
import socket
import threading
import json
import time

class XRServer(Module):
    """
    Dedicated server for Streaming World State to AR/VR clients.
    Uses a simple TCP JSON stream for this prototype.
    """
    def __init__(self, kernel, port=9000):
        super().__init__(kernel)
        self.port = port
        self.clients = []
        self.running = False
        self.sock = None

    def initialize(self):
        self.kernel.log("XRServer", "Initialized.")

    def start(self):
        self.running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen(5)
            self.kernel.log("XRServer", f"Listening on port {self.port}")
            
            # Accept Thread
            threading.Thread(target=self._accept_clients, daemon=True).start()
            # Broadcast Thread
            threading.Thread(target=self._broadcast_loop, daemon=True).start()
        except Exception as e:
            self.kernel.log("XRServer", f"Failed to start: {e}", level="error")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

    def _accept_clients(self):
        while self.running:
            try:
                client, addr = self.sock.accept()
                self.clients.append(client)
                self.kernel.log("XRServer", f"XR Client connected: {addr}")
                threading.Thread(target=self._handle_input, args=(client,), daemon=True).start()
            except:
                break

    def _handle_input(self, client):
        """Receive Headset/Hand pose updates."""
        try:
            buffer = ""
            while self.running:
                data = client.recv(1024)
                if not data: break
                buffer += data.decode('utf-8')
                
                # Assume newline delimited JSON
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        msg = json.loads(line)
                        if "type" in msg:
                            self._process_message(msg)
        except:
            pass
        finally:
            if client in self.clients: self.clients.remove(client)

    def _process_message(self, msg):
        # Handle Pose Updates
        if msg["type"] == "pose":
            # Update User Avatar in World Engine
            # self.kernel.dispatch("xr:pose_update", msg)
            pass
        elif msg["type"] == "anchor_found":
            sm = self.kernel.get_module("spatial_map")
            if sm:
                sm.register_anchor(msg["id"], msg["coords"])

    def _broadcast_loop(self):
        """Stream World State @ 10Hz"""
        while self.running:
            world = self.kernel.get_module("world")
            if world:
                # Serialize minimal state
                entities = []
                for uid, e in world.entity_manager.entities.items():
                    # Only send entities with transforms
                    t = e.get_component("Transform") # string lookup if dynamic?
                    # For prototype, we assume we have a way to get components easily
                    # We'll rely on our earlier serializer logic or simple dict
                    if hasattr(e, "components"):
                        comps = {}
                        for c_type, c in e.components.items():
                            if c_type.__name__ in ["Transform", "Mesh", "Light", "Name"]:
                                comps[c_type.__name__] = vars(c)
                        if comps:
                            entities.append({"uid": uid, "components": comps})
                
                state_msg = json.dumps({"type": "world_state", "entities": entities}) + "\n"
                
                # Send to all
                for c in self.clients[:]:
                    try:
                        c.send(state_msg.encode('utf-8'))
                    except:
                        self.clients.remove(c)
            
            time.sleep(0.1) # 10Hz
