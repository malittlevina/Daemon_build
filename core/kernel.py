import threading
import time
from typing import Dict, Any, Optional

from .events import EventBus, Event
from daemon.state_manager import StateManager
# from unimind.core import Unimind # Circular dependency risk?
# from nlu.nlu_engine import NLUEngine

class Kernel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Kernel, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        print("[Kernel] Initializing...")
        self.bus = EventBus()
        self.state_manager = StateManager()
        self.modules = {}
        self.running = False
        self.initialized = True
        
        # Core Context
        self.context = {
            "mode": "idle",
            "active_module": None,
            "last_interaction": 0
        }

    def register_module(self, name: str, module: Any):
        self.modules[name] = module
        print(f"[Kernel] Registered module: {name}")
        if hasattr(module, "register_events"):
            module.register_events(self.bus)

    def start(self):
        self.running = True
        self.bus.publish("kernel:start", {"timestamp": time.time()})
        print("[Kernel] System Started.")
        
        # Start background ticker
        self._ticker_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._ticker_thread.start()

    def stop(self):
        self.running = False
        self.bus.publish("kernel:stop", {})
        print("[Kernel] System Stopping...")

    def _tick_loop(self):
        while self.running:
            time.sleep(1) # 1Hz heartbeat
            self.bus.publish("kernel:heartbeat", {"tick": time.time()})

    def dispatch_input(self, user_input: str) -> str:
        self.context["last_interaction"] = time.time()
        self.bus.publish("input:received", {"text": user_input})
        
        # Route to NLU if available
        if "nlu" in self.modules:
            response = self.modules["nlu"].interpret(user_input)
            self.bus.publish("output:generated", {"text": response})
            return response
        
        return "[Kernel] NLU not active."

# Global Access
def get_kernel():
    return Kernel()
