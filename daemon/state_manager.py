from core.module import Module
import json
import os

class StateManager(Module):
    def __init__(self, kernel, state_file="config/state.json"):
        super().__init__(kernel)
        self.state_file = state_file
        self.state = {
            "is_paused": False,
            "last_run": None,
            "scroll_count": 0
        }

    def initialize(self):
        self._load_state()
        print("[StateManager] Initialized.")

    def start(self):
        pass

    def stop(self):
        self.save_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    self.state = json.load(f)
            except Exception as e:
                print(f"[StateManager] Error loading state: {e}")

    def save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def set(self, key, value):
        self.state[key] = value
        self.save_state()

    def get(self, key):
        return self.state.get(key)

    def toggle_pause(self):
        self.state["is_paused"] = not self.state["is_paused"]
        self.save_state()
        return self.state["is_paused"]
