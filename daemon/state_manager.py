# daemon/state_manager.py

import json
import os

class StateManager:
    def __init__(self, state_file="config/state.json"):
        self.state_file = state_file
        self.state = {
            "is_paused": False,
            "last_run": None,
            "scroll_count": 0
        }
        self._ensure_parent_dir()
        self._load_state()

    def _ensure_parent_dir(self):
        parent = os.path.dirname(self.state_file) or "."
        os.makedirs(parent, exist_ok=True)

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.state = json.load(f)

    def save_state(self):
        self._ensure_parent_dir()
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
