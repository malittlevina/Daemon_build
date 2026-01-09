from core.module import Module
import time
import uuid

class UserManager(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.current_user = None
        self.sessions = {}

    def initialize(self):
        self.registry = self.kernel.get_module("registry")
        self.kernel.log("UserManager", "Initialized.")
        
        # Ensure default admin exists
        if self.registry:
            if not self.registry.get("user:admin"):
                self.create_user("admin", "root", role="superuser")

    def start(self):
        pass

    def stop(self):
        pass

    def create_user(self, username, password, role="user"):
        if self.registry:
            user_data = {
                "username": username,
                "password": password, # In a real OS, hash this!
                "role": role,
                "created_at": time.time()
            }
            self.registry.set(f"user:{username}", user_data)
            self.kernel.log("UserManager", f"Created user: {username}")
    
    def login(self, username, password):
        if not self.registry:
            return None
            
        user_data = self.registry.get(f"user:{username}")
        if user_data and user_data["password"] == password:
            session_id = str(uuid.uuid4())
            session = {
                "id": session_id,
                "username": username,
                "role": user_data["role"],
                "login_time": time.time()
            }
            self.sessions[session_id] = session
            self.current_user = session
            self.kernel.log("UserManager", f"User {username} logged in.")
            return session
        
        self.kernel.log("UserManager", f"Failed login attempt for {username}", level="warning")
        return None

    def logout(self):
        if self.current_user:
            self.kernel.log("UserManager", f"User {self.current_user['username']} logged out.")
            self.current_user = None

    def get_current_user(self):
        return self.current_user or {"username": "guest", "role": "guest"}
