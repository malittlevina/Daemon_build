# daemon/state_manager.py

import json
import os
import platform

class StateManager:
    def __init__(self, state_file="config/state.json", config_file="config/daemon_config.json"):
        self.state_file = state_file
        self.config_file = config_file
        self.state = {
            "is_paused": False,
            "last_run": None,
            "scroll_count": 0
        }
        self.runtime_context = {
            "os_type": platform.system(),
            "is_native_os": False,
            "mode": "standard"
        }
        self._load_state()
        self._detect_environment()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.state = json.load(f)

    def _detect_environment(self):
        # Load config to check for native OS indicators
        config = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
        
        os_pref = config.get("os_preference", {})
        indicators = os_pref.get("native_indicators", [])
        
        is_native = False
        # Check environment variables
        for indicator in indicators:
            if indicator.startswith("/"):
                # File check
                if os.path.exists(indicator):
                    is_native = True
                    break
            else:
                # Env var check
                if indicator in os.environ:
                    is_native = True
                    break
        
        self.runtime_context["is_native_os"] = is_native
        if is_native and os_pref.get("prioritize_native", False):
            self.runtime_context["mode"] = "prioritized"
        else:
            self.runtime_context["mode"] = "compatibility"

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def set(self, key, value):
        self.state[key] = value
        self.save_state()

    def get(self, key):
        return self.state.get(key)
    
    def get_context(self):
        return self.runtime_context

    def toggle_pause(self):
        self.state["is_paused"] = not self.state["is_paused"]
        self.save_state()
        return self.state["is_paused"]
