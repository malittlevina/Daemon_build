from core.module import Module

class EmotionEngine(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.current_emotion = "neutral"

    def initialize(self):
        self.kernel.log("EmotionEngine", "Initialized.")
        self.kernel.events.subscribe("stimulus", self.handle_stimulus)

    def start(self):
        pass

    def stop(self):
        pass

    def handle_stimulus(self, event_type, data):
        self.update_emotion(data.get("trigger", ""))

    def update_emotion(self, stimulus):
        emotion_map = {
            "optimize self": "focused",
            "summon knowledge": "curious",
            "user praise": "proud",
            "error": "frustrated"
        }
        self.current_emotion = emotion_map.get(stimulus, "neutral")
        self.kernel.log("EmotionEngine", f"Emotion updated to: {self.current_emotion}")

    def get_emotion(self):
        return self.current_emotion

# Deprecated singleton, kept for backward compat if needed, but 'kernel' is required now.
# emotion_state = EmotionEngine() 
# def update_emotional_state(trigger: str):
#     emotion_state.update_emotion(trigger)
