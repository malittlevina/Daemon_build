import json
import os

class ConfigManager:
    def __init__(self, config_path="config/daemon_config.json"):
        self.config_path = config_path
        self.config = {}
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                print(f"[Config] Loaded configuration from {self.config_path}")
            except Exception as e:
                print(f"[Config] Error loading configuration: {e}")
        else:
            print(f"[Config] Warning: Config file not found at {self.config_path}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        # Optional: auto-save? For now, keep in memory or explicit save.
        
    def save(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            print(f"[Config] Saved configuration to {self.config_path}")
        except Exception as e:
            print(f"[Config] Error saving configuration: {e}")
