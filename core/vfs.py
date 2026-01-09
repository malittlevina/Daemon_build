from core.module import Module
import os
import shutil

class VFS(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.mounts = {}
        self.root_path = os.getcwd()
        self.protected_paths = ["core", "config", "guardian", "main.py"]

    def initialize(self):
        # Mount points
        self.mount("/", self.root_path)
        self.kernel.log("VFS", "Initialized. Root mounted.")

    def start(self):
        pass

    def stop(self):
        pass

    def mount(self, virtual_path, real_path):
        self.mounts[virtual_path] = real_path

    def _resolve(self, virtual_path):
        """Convert /home/doc.txt -> /workspace/users/home/doc.txt"""
        # Simplistic resolution for the prototype
        # In a real OS, this handles nested mounts.
        # Here we just treat everything relative to root workspace unless mounted otherwise.
        
        if virtual_path.startswith("/"):
            virtual_path = virtual_path[1:]
        
        real_path = os.path.abspath(os.path.join(self.root_path, virtual_path))
        
        # Security Sandbox check
        if not real_path.startswith(self.root_path):
            raise PermissionError("Access denied: Cannot access outside filesystem root.")
        
        return real_path

    def _check_permission(self, path, mode="r"):
        users = self.kernel.get_module("users")
        if not users: return True # No user system loaded, allow all (boot mode)
        
        user = users.get_current_user()
        role = user.get("role", "guest")
        
        # Admin can do anything
        if role == "superuser":
            return True
            
        # Protect System Files
        for protected in self.protected_paths:
            if protected in path:
                if mode == "w": return False # Read-only for system files
        
        return True

    # --- Public File API ---

    def list_dir(self, path="."):
        real_path = self._resolve(path)
        if not self._check_permission(real_path, "r"):
            return "Permission Denied."
        
        if os.path.exists(real_path) and os.path.isdir(real_path):
            return os.listdir(real_path)
        return "Path not found or not a directory."

    def read_file(self, path):
        real_path = self._resolve(path)
        if not self._check_permission(real_path, "r"):
            return "Permission Denied."
            
        try:
            with open(real_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, path, content):
        real_path = self._resolve(path)
        if not self._check_permission(real_path, "w"):
            return "Permission Denied."
            
        try:
            with open(real_path, "w") as f:
                f.write(content)
            return "File written successfully."
        except Exception as e:
            return f"Error writing file: {e}"

    def delete(self, path):
        real_path = self._resolve(path)
        if not self._check_permission(real_path, "w"):
            return "Permission Denied."
            
        try:
            if os.path.isdir(real_path):
                shutil.rmtree(real_path)
            else:
                os.remove(real_path)
            return "Deleted."
        except Exception as e:
            return f"Error deleting: {e}"
