from core.module import Module
import os
import subprocess

class IDE(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.workspace_root = os.getcwd()
        self.open_files = {} # path -> content
        self.active_file = None

    def initialize(self):
        self.kernel.log("IDE", "Initialized.")

    def start(self):
        pass

    def stop(self):
        pass

    def open_file(self, path):
        """Open a file into the IDE buffer."""
        full_path = os.path.abspath(path)
        if not full_path.startswith(self.workspace_root):
            return "Security Restriction: Cannot open files outside workspace."
        
        try:
            with open(full_path, "r") as f:
                content = f.read()
            self.open_files[path] = content
            self.active_file = path
            self.kernel.log("IDE", f"Opened file: {path}")
            return f"Opened {path}. {len(content.splitlines())} lines."
        except FileNotFoundError:
            return f"File not found: {path}"
        except Exception as e:
            return f"Error opening file: {e}"

    def write_file(self, path, content):
        """Write content to file."""
        full_path = os.path.abspath(path)
        if not full_path.startswith(self.workspace_root):
            return "Security Restriction: Cannot write files outside workspace."
            
        try:
            with open(full_path, "w") as f:
                f.write(content)
            self.open_files[path] = content
            self.kernel.log("IDE", f"Saved file: {path}")
            return f"Saved {path}."
        except Exception as e:
            return f"Error saving file: {e}"

    def list_files(self, directory="."):
        try:
            items = os.listdir(directory)
            files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
            dirs = [d for d in items if os.path.isdir(os.path.join(directory, d))]
            return f"Directories: {dirs}\nFiles: {files}"
        except Exception as e:
            return f"Error listing directory: {e}"

    def run_script(self, path):
        """Execute a Python script."""
        full_path = os.path.abspath(path)
        if not full_path.startswith(self.workspace_root):
            return "Security Restriction."
        
        self.kernel.log("IDE", f"Executing script: {path}")
        try:
            # Basic subprocess execution
            result = subprocess.run(
                ["python3", full_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nERR: {result.stderr}"
            return output
        except subprocess.TimeoutExpired:
            return "Execution timed out."
        except Exception as e:
            return f"Execution error: {e}"
