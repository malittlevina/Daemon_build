import time
import math

class EmotionEngine:
    def __init__(self):
        # PAD Model: Pleasure, Arousal, Dominance
        # Scale: -1.0 to 1.0
        self.state = {
            "pleasure": 0.0,
            "arousal": 0.0,
            "dominance": 0.0
        }
        self.last_update_time = time.time()
        
        # Base temperament (the state the system returns to)
        self.baseline = {
            "pleasure": 0.1,  # Slightly positive
            "arousal": 0.0,   # Calm
            "dominance": 0.1  # Slightly confident
        }
        
        # Decay rate (how fast it returns to baseline per second)
        self.decay_rate = 0.05

    def _apply_decay(self):
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        self.last_update_time = current_time
        
        for dim in ["pleasure", "arousal", "dominance"]:
            diff = self.baseline[dim] - self.state[dim]
            # Exponential decay toward baseline
            change = diff * (1 - math.exp(-self.decay_rate * elapsed))
            self.state[dim] += change

    def update_emotion(self, stimulus, intensity=0.2):
        self._apply_decay()
        
        # Stimulus mapping to PAD changes
        # (Pleasure change, Arousal change, Dominance change)
        stimulus_map = {
            "optimize self": (0.2, 0.3, 0.4),      # Exciting, empowering
            "summon knowledge": (0.1, 0.1, 0.2),   # Helpful, confident
            "user praise": (0.4, 0.2, -0.1),       # Happy, submissive (grateful)
            "error": (-0.3, 0.4, -0.2),            # Unhappy, stressed, helpless
            "success": (0.3, 0.1, 0.2),            # Happy, calm, confident
            "confusion": (-0.1, 0.3, -0.3),        # Slightly unhappy, active, submissive
            "threat": (-0.5, 0.8, -0.4),           # Fear: Unhappy, very active, submissive
            "challenge": (0.1, 0.6, 0.1)           # Excitement/Interest
        }
        
        delta = stimulus_map.get(stimulus, (0, 0, 0))
        
        self.state["pleasure"] = max(-1.0, min(1.0, self.state["pleasure"] + delta[0] * intensity))
        self.state["arousal"] = max(-1.0, min(1.0, self.state["arousal"] + delta[1] * intensity))
        self.state["dominance"] = max(-1.0, min(1.0, self.state["dominance"] + delta[2] * intensity))
        
        named = self.get_emotion_name()
        print(f"[EmotionEngine] Stimulus: '{stimulus}' -> New State: {named} (P:{self.state['pleasure']:.2f}, A:{self.state['arousal']:.2f}, D:{self.state['dominance']:.2f})")

    def get_emotion_name(self):
        # Simplified mapping of PAD quadrants/octants to names
        p, a, d = self.state["pleasure"], self.state["arousal"], self.state["dominance"]
        
        if p > 0.5 and a > 0.5: return "Ecstatic"
        if p > 0.5 and a < -0.2: return "Serene"
        if p < -0.5 and a > 0.5: return "Furious" if d > 0 else "Terrified"
        if p < -0.5 and a < -0.2: return "Depressed"
        
        if p > 0.1:
            if a > 0.1: return "Happy"
            return "Content"
        if p < -0.1:
            if a > 0.1: return "Anxious"
            return "Sad"
            
        if a > 0.3: return "Alert"
        if a < -0.3: return "Bored"
        
        return "Neutral"

    def get_emotion(self):
        self._apply_decay()
        return self.get_emotion_name()

# Singleton instance
emotion_state = EmotionEngine()

def update_emotional_state(trigger: str):
    emotion_state.update_emotion(trigger)
