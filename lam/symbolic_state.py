from core.module import Module

class SymbolicLayer(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.state = {
            "history": [],
            "current_context": {},
            "flags": {}
        }

    def initialize(self):
        self.kernel.log("SymbolicLayer", "Initialized.")
        self.kernel.events.subscribe("user_input", self.handle_input_event)

    def start(self):
        pass

    def stop(self):
        pass

    def handle_input_event(self, event_type, data):
        # data might be a dict {"text": "...", "result": "..."} or just text?
        # Main.py sends: {"text": user_input, "result": result}
        text = data.get("text", "")
        if text:
            self.update_state_with_input(text)

    def update_state_with_input(self, user_input):
        try:
            # Log input history
            self.state["history"].append(user_input)
            self.state["last_input"] = user_input

            # Basic symbolic parsing
            if "learn" in user_input.lower():
                self.state["current_context"]["mode"] = "learning"
                self.state["flags"]["is_learning"] = True
            elif "task" in user_input.lower():
                self.state["current_context"]["mode"] = "task_execution"
                self.state["flags"]["has_active_task"] = True
            else:
                self.state["current_context"]["mode"] = "idle"
                self.state["flags"].clear()

            self.kernel.log("SymbolicLayer", f"Updated state: {self.state}")
            return self.state

        except Exception as e:
            self.kernel.log("SymbolicLayer", f"Failed to update state: {e}", level="error")
            return None

    def get_state(self):
        return self.state

# Backward compatibility stub if needed, but we should migrate.
# But since we are polishing, let's try to remove global dependencies.
