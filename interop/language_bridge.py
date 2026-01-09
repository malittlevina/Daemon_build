import subprocess
import os
import platform

class LanguageBridge:
    def __init__(self):
        self.available_languages = ["python", "rust", "julia"]
        self.is_windows = platform.system() == "Windows"

    def execute_code(self, code: str, lang: str) -> str:
        if lang == "python":
            return self._exec_python(code)
        elif lang == "rust":
            return self._exec_rust(code)
        elif lang == "julia":
            return self._exec_julia(code)
        else:
            return f"[Bridge] Unsupported language: {lang}"

    def _exec_python(self, code):
        try:
            local_env = {}
            exec(code, {}, local_env)
            return str(local_env)
        except Exception as e:
            return f"[Python Error] {e}"

    def _exec_rust(self, code):
        try:
            # Use appropriate executable name
            exe_name = "temp_exec.exe" if self.is_windows else "temp_exec"
            source_name = "temp.rs"
            
            with open(source_name, "w") as f:
                f.write(code)
            
            # Compile
            compile_cmd = ["rustc", source_name, "-o", exe_name]
            subprocess.run(compile_cmd, check=True)
            
            # Execute
            exec_cmd = [f".{os.sep}{exe_name}"] if not self.is_windows else [exe_name]
            result = subprocess.run(exec_cmd, capture_output=True, text=True)
            
            # Cleanup
            if os.path.exists(source_name): os.remove(source_name)
            if os.path.exists(exe_name): os.remove(exe_name)
            if self.is_windows and os.path.exists("temp_exec.pdb"): os.remove("temp_exec.pdb")

            return result.stdout
        except subprocess.CalledProcessError:
            return "[Rust Error] Compilation failed."
        except Exception as e:
            return f"[Rust Error] {e}"

    def _exec_julia(self, code):
        try:
            # Check if Julia is installed
            import shutil
            if not shutil.which("julia"):
                return "[Bridge] Julia not found in PATH."

            result = subprocess.run(["julia", "-e", code], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"[Julia Error] {e}"
