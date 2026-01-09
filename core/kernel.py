import threading
import time
from core.event_bus import EventBus
from core.config import ConfigManager
from core.logger import SystemLogger

class Kernel:
    def __init__(self):
        # 1. Initialize Infrastructure
        self.config = ConfigManager()
        self.logger = SystemLogger()
        self.events = EventBus()
        
        self.modules = {}
        self.running = False
        
        self.log("Kernel", "Kernel Infrastructure Initialized.")

    def handle_panic(self, module_name, exception):
        """Global Panic Handler."""
        self.log("Kernel", f"PANIC in {module_name}: {exception}", level="critical")
        # Could trigger safe mode or restart module
        homeostasis = self.get_module("homeostasis")
        if homeostasis:
            # Manually inject error logic since we don't have a direct method exposed
            homeostasis.error_count += 1
            homeostasis.health_score -= 20

    def log(self, source, message, level="info"):
        if level == "info":
            self.logger.info(source, message)
        elif level == "warning":
            self.logger.warning(source, message)
        elif level == "error":
            self.logger.error(source, message)
        elif level == "debug":
            self.logger.debug(source, message)

    def register_module(self, name, module_instance):
        self.modules[name] = module_instance
        self.log("Kernel", f"Registered module: {name}")

    def get_module(self, name):
        return self.modules.get(name)

    def initialize(self):
        self.log("Kernel", "Initializing modules...")
        for name, module in self.modules.items():
            try:
                module.initialize()
            except Exception as e:
                self.log("Kernel", f"Error initializing {name}: {e}", level="error")

    def start(self):
        self.log("Kernel", "Starting services...")
        self.running = True
        for name, module in self.modules.items():
            try:
                module.start()
            except Exception as e:
                self.log("Kernel", f"Error starting {name}: {e}", level="error")
        
        # Publish startup event
        self.events.publish("kernel:startup", {"timestamp": time.time()})

    def stop(self):
        self.log("Kernel", "Stopping services...")
        self.running = False
        self.events.publish("kernel:shutdown", {"timestamp": time.time()})
        
        # Stop in reverse order of registration (heuristic)
        for name, module in reversed(list(self.modules.items())):
            try:
                module.stop()
            except Exception as e:
                self.log("Kernel", f"Error stopping {name}: {e}", level="error")

    def dispatch(self, event_type, data=None):
        # Optional: Log all events? Might be noisy.
        # self.log("Kernel", f"Dispatching: {event_type}") 
        self.events.publish(event_type, data)
