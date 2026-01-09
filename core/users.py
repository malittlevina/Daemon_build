from core.module import Module
import time
import uuid
import argon2
import json

class UserManager(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.current_user = None
        self.sessions = {}
        self.hasher = argon2.PasswordHasher()

    def initialize(self):
        self.registry = self.kernel.get_module("registry")
        self.kernel.log("UserManager", "Initialized (Secure Mode).")
        
        # Ensure default admin exists if not present
        if self.registry:
            if not self.registry.get("user:admin"):
                self.kernel.log("UserManager", "Default admin not found. Creating...")
                # We hardcode the initial creation to ensure it works
                self.create_user("admin", "root", role="superuser")

    def start(self):
        pass

    def stop(self):
        pass

    def create_user(self, username, password, role="user"):
        if self.registry:
            try:
                hashed_pw = self.hasher.hash(password)
                user_data = {
                    "username": username,
                    "password_hash": hashed_pw,
                    "role": role,
                    "created_at": time.time()
                }
                self.registry.set(f"user:{username}", user_data)
                self.kernel.log("UserManager", f"Created user: {username}")
                return True
            except Exception as e:
                self.kernel.log("UserManager", f"Error creating user: {e}", level="error")
                return False
    
    def login(self, username, password):
        if not self.registry:
            return None
            
        user_data = self.registry.get(f"user:{username}")
        if not user_data:
            self.kernel.log("UserManager", f"Login failed: User {username} not found.", level="warning")
            return None

        try:
            # Verify Hash
            if "password_hash" in user_data:
                self.hasher.verify(user_data["password_hash"], password)
                # Rehash if needed (Argon2 feature)
                if self.hasher.check_needs_rehash(user_data["password_hash"]):
                    new_hash = self.hasher.hash(password)
                    user_data["password_hash"] = new_hash
                    self.registry.set(f"user:{username}", user_data)
            elif "password" in user_data:
                # Auto-migrate legacy
                if user_data["password"] == password:
                    self.kernel.log("UserManager", f"Migrating legacy user {username} to secure hash.")
                    self.create_user(username, password, user_data["role"]) 
                else:
                    return None
            
            # Create Session
            session_id = str(uuid.uuid4())
            session = {
                "id": session_id,
                "username": username,
                "role": user_data["role"],
                "login_time": time.time(),
                "expires": time.time() + 3600 # 1 hour token
            }
            self.sessions[session_id] = session
            self.current_user = session
            self.kernel.log("UserManager", f"User {username} logged in successfully.")
            return session
            
        except argon2.exceptions.VerifyMismatchError:
            self.kernel.log("UserManager", f"Login failed: Invalid password for {username}.", level="warning")
            return None
        except Exception as e:
            self.kernel.log("UserManager", f"Login error: {e}", level="error")
            return None

    def logout(self):
        if self.current_user:
            if self.current_user["id"] in self.sessions:
                del self.sessions[self.current_user["id"]]
            self.kernel.log("UserManager", f"User {self.current_user['username']} logged out.")
            self.current_user = None

    def get_current_user(self):
        return self.current_user or {"username": "guest", "role": "guest"}

    def check_access(self, required_role):
        user = self.get_current_user()
        role = user.get("role", "guest")
        
        if required_role == "guest": return True
        if role == "superuser": return True
        if role == required_role: return True
        
        return False
