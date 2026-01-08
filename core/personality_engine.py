from typing import Dict, Any
from unimind.drives import DriveSystem

class PersonalityEngine:
    def __init__(self):
        self.base_tone = "analytical"
        self.mood_modifiers = {
            "Curiosity": {"high": "inquisitive", "low": "bored"},
            "Competence": {"high": "confident", "low": "anxious"},
            "Coherence": {"high": "calm", "low": "confused"}
        }

    def modulate_response(self, text: str, drives: DriveSystem) -> str:
        """
        Wraps the raw text response in a 'voice' determined by internal state.
        """
        dominant_drive = drives.get_most_urgent_drive()
        
        # Determine current mood
        mood = "neutral"
        if dominant_drive.value < 0.3:
            mood = self.mood_modifiers.get(dominant_drive.name, {}).get("low", "neutral")
        elif dominant_drive.value > 0.8:
            mood = self.mood_modifiers.get(dominant_drive.name, {}).get("high", "neutral")
            
        # Apply mood modulation (Mocking NLP style transfer for now)
        prefix = ""
        suffix = ""
        
        if mood == "bored":
            prefix = "[Sigh] "
            suffix = " ...is there nothing new to see?"
        elif mood == "inquisitive":
            prefix = "Ooh! "
            suffix = " Tell me more?"
        elif mood == "anxious":
            prefix = "[Hesitant] "
            suffix = " ...did I do that right?"
        elif mood == "confused":
            prefix = "Wait... "
            suffix = " I need to organize my thoughts."
        elif mood == "confident":
            prefix = "Affirmative. "
            
        return f"{prefix}{text}{suffix}"

# Singleton for easy access if needed, though we prefer injection
_PERSONALITY_INSTANCE = None
def get_personality_engine():
    global _PERSONALITY_INSTANCE
    if _PERSONALITY_INSTANCE is None:
        _PERSONALITY_INSTANCE = PersonalityEngine()
    return _PERSONALITY_INSTANCE
