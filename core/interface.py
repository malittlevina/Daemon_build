from core.module import Module
import socket
import threading
import json

class Interface(Module):
    def __init__(self, kernel, host='127.0.0.1', port=9999):
        super().__init__(kernel)
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []

    def initialize(self):
        self.kernel.log("Interface", "Initialized.")

    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.kernel.log("Interface", f"Listening on {self.host}:{self.port}")
            
            # Start listener thread
            self.thread = threading.Thread(target=self._accept_clients, daemon=True)
            self.thread.start()
        except Exception as e:
            self.kernel.log("Interface", f"Failed to bind port: {e}", level="error")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.kernel.log("Interface", "Stopped.")

    def _accept_clients(self):
        while self.running:
            try:
                client, addr = self.server_socket.accept()
                self.kernel.log("Interface", f"Connection from {addr}")
                self.clients.append(client)
                client_handler = threading.Thread(target=self._handle_client, args=(client,), daemon=True)
                client_handler.start()
            except OSError:
                break

    def _handle_client(self, client):
        try:
            while self.running:
                data = client.recv(1024)
                if not data:
                    break
                
                command = data.decode('utf-8').strip()
                if command:
                    self.kernel.log("Interface", f"Received command: {command}")
                    # Dispatch to Kernel
                    self.kernel.dispatch("user_input", {"text": command, "source": "api"})
                    
                    # Send ACK
                    response = json.dumps({"status": "received", "command": command}) + "\n"
                    client.send(response.encode('utf-8'))
        except Exception as e:
            self.kernel.log("Interface", f"Client error: {e}", level="error")
        finally:
            client.close()
            if client in self.clients:
                self.clients.remove(client)
