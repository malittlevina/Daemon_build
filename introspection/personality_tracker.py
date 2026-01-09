from core.module import Module
import json
import datetime
from codex.ingestion import ingest_observation

class PersonalityTracker(Module):
    def __init__(self, kernel, log_path="introspection/personality_log.json"):
        super().__init__(kernel)
        self.log_path = log_path
        self.current_traits = {}

    def initialize(self):
        self.kernel.log("PersonalityTracker", "Initialized.")
        self.load()

    def start(self):
        pass

    def stop(self):
        pass

    def load(self):
        try:
            with open(self.log_path, "r") as f:
                # Assuming JSON lines format or single object.
                # Original code seemed to mix them (load reads JSON, append writes JSON lines).
                # We'll stick to JSON lines for append, but load might need care.
                # If load fails as simple JSON, try parsing lines.
                content = f.read()
                if not content:
                    self.current_traits = {}
                    return
                try:
                    self.current_traits = json.loads(content)
                except json.JSONDecodeError:
                    # Maybe it's a log file of lines? Reconstruct state from lines.
                    self.current_traits = {}
                    for line in content.splitlines():
                        if line:
                            entry = json.loads(line)
                            if "trait" in entry:
                                self.current_traits[entry["trait"]] = entry["value"]
        except FileNotFoundError:
            self.current_traits = {}

    def log_trait_change(self, trait, value):
        timestamp = datetime.datetime.now().isoformat()
        entry = {"timestamp": timestamp, "trait": trait, "value": value}
        self.current_traits[trait] = value
        self._append_log(entry)

    def _append_log(self, entry):
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[PersonalityTracker] Error logging trait: {e}")

    def get_traits(self):
        return self.current_traits

    def log_state(self):
        timestamp = datetime.datetime.now().isoformat()
        state_snapshot = {
            "timestamp": timestamp,
            "current_traits": self.current_traits
        }
        self.kernel.log("PersonalityTracker", f"Current state: {json.dumps(state_snapshot, indent=2)}")
        ingest_observation(f"Personality state logged: {json.dumps(self.current_traits)}")
