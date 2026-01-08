import threading
import time
from core.event_bus import EventBus

class Kernel:
    def __init__(self):
        self.events = EventBus()
        self.modules = {}
        self.running = False
        self._thread = None

    def register_module(self, name, module_instance):
        self.modules[name] = module_instance
        print(f"[Kernel] Registered module: {name}")

    def get_module(self, name):
        return self.modules.get(name)

    def initialize(self):
        print("[Kernel] Initializing modules...")
        for name, module in self.modules.items():
            try:
                module.initialize()
            except Exception as e:
                print(f"[Kernel] Error initializing {name}: {e}")

    def start(self):
        print("[Kernel] Starting services...")
        self.running = True
        for name, module in self.modules.items():
            try:
                module.start()
            except Exception as e:
                print(f"[Kernel] Error starting {name}: {e}")
        
        # Publish startup event
        self.events.publish("kernel:startup", {"timestamp": time.time()})

    def stop(self):
        print("[Kernel] Stopping services...")
        self.running = False
        self.events.publish("kernel:shutdown", {"timestamp": time.time()})
        
        # Stop in reverse order of registration (heuristic)
        for name, module in reversed(list(self.modules.items())):
            try:
                module.stop()
            except Exception as e:
                print(f"[Kernel] Error stopping {name}: {e}")

    def dispatch(self, event_type, data=None):
        self.events.publish(event_type, data)
