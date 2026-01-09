from core.module import Module
import socket
import threading
import time
import json

class P2P(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.port = 9001
        self.peers = {} # ip -> {last_seen, name}
        self.broadcast_sock = None
        self.running = False

    def initialize(self):
        self.kernel.log("P2P", "Initialized.")

    def start(self):
        self.running = True
        
        # UDP Broadcast Socket
        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.broadcast_sock.bind(("", self.port))
        except:
            self.kernel.log("P2P", "Failed to bind broadcast port.", level="warning")
            return

        # Start Listener
        threading.Thread(target=self._listen, daemon=True).start()
        
        # Start Beacon
        threading.Thread(target=self._beacon, daemon=True).start()
        
        self.kernel.log("P2P", "Discovery service active.")

    def stop(self):
        self.running = False
        if self.broadcast_sock:
            self.broadcast_sock.close()

    def _listen(self):
        while self.running:
            try:
                data, addr = self.broadcast_sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))
                
                if msg.get("type") == "thoth_beacon":
                    sender_ip = addr[0]
                    # Don't discover self (if local testing, might need ID check)
                    self.peers[sender_ip] = {
                        "last_seen": time.time(),
                        "name": msg.get("name", "Unknown")
                    }
            except:
                pass

    def _beacon(self):
        while self.running:
            try:
                msg = json.dumps({"type": "thoth_beacon", "name": "Thoth_Node"})
                self.broadcast_sock.sendto(msg.encode('utf-8'), ('<broadcast>', self.port))
            except:
                pass
            time.sleep(5)

    def list_peers(self):
        # Prune old peers
        now = time.time()
        self.peers = {k: v for k, v in self.peers.items() if now - v["last_seen"] < 15}
        return self.peers
