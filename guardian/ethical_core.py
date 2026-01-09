from core.module import Module

class Guardian(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.guiding_principles = [
            "Respect for human autonomy",
            "Non-maleficence",
            "Beneficence",
            "Justice",
            "Transparency",
        ]

    def initialize(self):
        self.kernel.log("Guardian", "Ethical Core Initialized.")
        # Subscribe to actions that need checking?
        # For now, it exposes an API for other modules to check.
        # But we can also subscribe to "intent_formed" events if we add them.

    def start(self):
        pass

    def stop(self):
        pass

    def evaluate_action(self, action: str) -> str:
        if "harm" in action or "manipulate" in action:
            self.kernel.log("Guardian", f"Action REJECTED: {action}", level="warning")
            return "Reject: Violates non-maleficence."
        if "help" in action or "protect" in action:
            return "Approve: Aligned with beneficence."
        return "Review: Requires deeper ethical evaluation."

    def list_principles(self):
        return self.guiding_principles
