from core.module import Module
import importlib
import sys
import os
import shutil

class PackageManager(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.packages_dir = "packages"
        self.installed_modules = {}

    def initialize(self):
        os.makedirs(self.packages_dir, exist_ok=True)
        # Add packages dir to path so we can import from it
        sys.path.append(os.path.abspath(self.packages_dir))
        self.kernel.log("PackageManager", "Initialized.")
        self._load_installed_packages()

    def start(self):
        pass

    def stop(self):
        pass

    def _load_installed_packages(self):
        """Scan packages dir and attempt to register found modules."""
        # Simple convention: packages/my_module/main.py -> class MyModule(Module)
        # For now, we stub this dynamic loading logic.
        pass

    def install(self, package_name, source_code=None):
        """Install a new module from code."""
        # This allows the AI to write its own extensions and install them.
        try:
            pkg_path = os.path.join(self.packages_dir, package_name)
            os.makedirs(pkg_path, exist_ok=True)
            
            file_path = os.path.join(pkg_path, "__init__.py")
            if source_code:
                with open(file_path, "w") as f:
                    f.write(source_code)
                self.kernel.log("PackageManager", f"Installed package '{package_name}' to {pkg_path}")
                return f"Installed {package_name}"
            else:
                return "No source code provided."
        except Exception as e:
            return f"Installation failed: {e}"

    def list_packages(self):
        return os.listdir(self.packages_dir)

    def load_dynamic_module(self, package_name, class_name):
        """Dynamically load and register a module from the packages dir."""
        try:
            module = importlib.import_module(f"{package_name}")
            # Re-import to ensure fresh code
            importlib.reload(module)
            
            cls = getattr(module, class_name)
            instance = cls(self.kernel)
            
            self.kernel.register_module(package_name, instance)
            instance.initialize()
            instance.start()
            
            return f"Loaded module {package_name}"
        except Exception as e:
            self.kernel.log("PackageManager", f"Failed to load {package_name}: {e}", level="error")
            return f"Error: {e}"
