# emotion/emotion_engine.py

class EmotionEngine:
    def __init__(self):
        self.current_emotion = "neutral"

        # Subscribe to relevant events
        if hasattr(unimind, "subscribe"):
            unimind.subscribe("input_received", self.update_emotion)
            unimind.subscribe("thought_generated", self.update_emotion)
    
    def update_emotion(self, stimulus):
        # Handle dict payloads from event bus
        if isinstance(stimulus, dict):
            stimulus = stimulus.get("content") or stimulus.get("text") or "unknown"

        emotion_map = {
            "optimize self": "focused",
            "summon knowledge": "curious",
            "user praise": "proud",
            "error": "frustrated"
        }
        # Simple keyword matching for now
        for key in emotion_map:
            if key in str(stimulus).lower():
                self.current_emotion = emotion_map[key]
                print(f"[EmotionEngine] Emotion updated to: {self.current_emotion}")
                return

        # Default minimal update
        # print(f"[EmotionEngine] Processing stimulus: {stimulus}")

    def get_emotion(self):
        return self.current_emotion

emotion_state = EmotionEngine()

def update_emotional_state(trigger: str):
    emotion_state.update_emotion(trigger)
