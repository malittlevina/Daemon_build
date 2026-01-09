from core.module import Module
import socket
import threading
import ipaddress
import time

class NetworkManager(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.active_connections = {} # socket_id -> {socket, address, type}
        self.firewall_rules = [] # List of {"type": "ALLOW/DENY", "ip": "...", "port": ...}
        self.lock = threading.Lock()
        self.dns_cache = {}

    def initialize(self):
        # Default Firewall Rules
        self.add_rule("ALLOW", "127.0.0.1", "*") # Allow localhost
        self.kernel.log("NetworkManager", "Initialized. Default firewall active.")

    def start(self):
        pass

    def stop(self):
        # Close all active connections
        with self.lock:
            for sock_id, conn in self.active_connections.items():
                try:
                    conn["socket"].close()
                except:
                    pass
        self.kernel.log("NetworkManager", "Stopped. Closed all connections.")

    def add_rule(self, action, ip, port):
        """Add a firewall rule."""
        self.firewall_rules.append({"action": action, "ip": ip, "port": port})
        self.kernel.log("NetworkManager", f"Firewall rule added: {action} {ip}:{port}")

    def check_firewall(self, ip, port):
        """Check if an outgoing/incoming connection is allowed."""
        # Simple deny-all-unless-allowed logic or allow-all-unless-denied?
        # Let's go with Allow All unless Denied for outbound (client), 
        # but Deny All inbound unless Allowed (server).
        
        # For this prototype, we just log checks.
        # In a real system, we'd match IP ranges/CIDR.
        return True 

    def create_socket(self, type="tcp"):
        """Create a managed socket."""
        sock_type = socket.SOCK_STREAM if type == "tcp" else socket.SOCK_DGRAM
        sock = socket.socket(socket.AF_INET, sock_type)
        
        sock_id = id(sock)
        with self.lock:
            self.active_connections[sock_id] = {
                "socket": sock,
                "created_at": time.time(),
                "type": type,
                "status": "created"
            }
        
        return sock

    def connect(self, sock, host, port):
        """Managed connect wrapper."""
        if not self.check_firewall(host, port):
            raise ConnectionRefusedError(f"Firewall blocked connection to {host}:{port}")

        try:
            sock.connect((host, port))
            with self.lock:
                if id(sock) in self.active_connections:
                    self.active_connections[id(sock)]["status"] = "connected"
                    self.active_connections[id(sock)]["remote"] = f"{host}:{port}"
            self.kernel.log("NetworkManager", f"Connected to {host}:{port}")
        except Exception as e:
            self.kernel.log("NetworkManager", f"Connection failed: {e}", level="error")
            raise e

    def resolve(self, hostname):
        """DNS Resolution with caching."""
        if hostname in self.dns_cache:
            # Check expiry? For now simple cache
            return self.dns_cache[hostname]
        
        try:
            ip = socket.gethostbyname(hostname)
            self.dns_cache[hostname] = ip
            return ip
        except Exception as e:
            self.kernel.log("NetworkManager", f"DNS Lookup failed for {hostname}: {e}", level="error")
            return None

    def get_status(self):
        with self.lock:
            return {
                "active_connections": len(self.active_connections),
                "firewall_rules": len(self.firewall_rules),
                "dns_cache_size": len(self.dns_cache)
            }
