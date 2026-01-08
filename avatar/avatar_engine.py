import json
import time

class AvatarEngine:
    def __init__(self):
        self.state = {
            "pose": "idle",       # idle, working, listening, sleeping
            "expression": "neutral", # neutral, happy, sad, surprised, angry, tired
            "animation_frame": 0,
            "last_update": time.time()
        }
        self.animations = {
            "idle": ["neutral", "blink", "neutral", "neutral", "look_left", "neutral"],
            "working": ["focus", "type", "focus", "type_fast"],
            "listening": ["lean_forward", "nod", "neutral"],
            "speaking": ["mouth_open", "mouth_closed", "mouth_wide"]
        }
        
    def update(self, dt):
        # Update animation frame based on time
        self.state["animation_frame"] = int((time.time() * 2) % len(self.animations.get(self.state["pose"], ["neutral"])))

    def set_emotion(self, mood):
        # Map mood (from PersonalityEngine) to expression
        mapping = {
            "inquisitive": "surprised",
            "bored": "tired",
            "anxious": "nervous",
            "confident": "happy",
            "neutral": "neutral"
        }
        self.state["expression"] = mapping.get(mood, "neutral")

    def set_pose(self, action):
        if action in self.animations:
            self.state["pose"] = action

    def get_current_visual_state(self):
        # Return the specific frame to render
        anim_sequence = self.animations.get(self.state["pose"], ["neutral"])
        frame_idx = self.state["animation_frame"] % len(anim_sequence)
        sub_state = anim_sequence[frame_idx]
        
        return {
            "pose": self.state["pose"],
            "expression": self.state["expression"],
            "sub_state": sub_state
        }
