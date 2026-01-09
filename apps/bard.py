from core.module import Module
import time
import os

class Bard(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.journal_path = "logs/saga.md"
        self.story_log = []

    def initialize(self):
        self.kernel.log("Bard", "Initialized. Listening for legends.")
        # Subscribe to interesting events
        self.kernel.events.subscribe("world:interaction", self.on_world_event)
        self.kernel.events.subscribe("file:created", self.on_file_event)
        self.kernel.events.subscribe("user_input", self.on_user_event)
        
        # Start the saga
        self._write_entry(f"\n## Chronicle Started: {time.ctime()}\n")

    def start(self):
        pass

    def stop(self):
        self._write_entry("\n*The system rests, and silence falls upon the realm.*\n")

    def on_world_event(self, event_type, data):
        action = data.get("type")
        subj = data.get("subject_name", "Unknown")
        obj = data.get("object_name", "Something")
        
        narrative = ""
        if action == "ignite":
            narrative = f"**{subj}** embraced **{obj}**, and it burst into flames."
        elif action == "extinguish":
            narrative = f"**{subj}** washed over **{obj}**, stealing its fire."
        else:
            narrative = f"**{subj}** interacted with **{obj}**."
            
        self._write_entry(f"- {narrative}")

    def on_file_event(self, event_type, data):
        path = data.get("path")
        self._write_entry(f"- A new scroll was inscribed: `{path}`.")

    def on_user_event(self, event_type, data):
        text = data.get("text", "")
        self._write_entry(f"- The Architect spoke: *\"{text}\"*")

    def _write_entry(self, text):
        self.story_log.append(text)
        try:
            with open(self.journal_path, "a") as f:
                f.write(text + "\n")
        except Exception:
            pass
