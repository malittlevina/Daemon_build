from core.module import Module

class Clipboard(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.content = None
        self.history = []

    def initialize(self):
        self.kernel.log("Clipboard", "Initialized.")

    def start(self):
        pass

    def stop(self):
        pass

    def copy(self, data):
        self.content = data
        self.history.append(data)
        # Keep history small
        if len(self.history) > 10:
            self.history.pop(0)
        self.kernel.log("Clipboard", f"Copied: {str(data)[:20]}...")
        return "Copied."

    def paste(self):
        return self.content if self.content is not None else ""

    def clear(self):
        self.content = None
        self.history = []
        return "Clipboard cleared."
