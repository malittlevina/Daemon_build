import time
import random
import threading

class PersistentAvatar:
    def __init__(self, ar_manager, emotion_engine):
        self.ar_manager = ar_manager
        self.emotion_engine = emotion_engine
        self.state = "IDLE"  # IDLE, OBSERVING, INTERACTING
        self.position = [0, 0, 0]
        self.last_action_time = time.time()
        self.active = False
        self.thread = None

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=self._behavior_loop, daemon=True)
        self.thread.start()
        print("[PersistentAvatar] Avatar materialized in AR space.")

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join(timeout=1)
        print("[PersistentAvatar] Avatar dematerialized.")

    def _behavior_loop(self):
        while self.active:
            current_time = time.time()
            if self.state == "IDLE":
                if current_time - self.last_action_time > 8: # Every 8 seconds
                     self._perform_ambient_action()
            
            # Simulate sensing environment even when idle
            self._scan_surroundings()
            
            time.sleep(1)

    def _perform_ambient_action(self):
        actions = [
            "examines its own hands", 
            "looks up at the ceiling", 
            "floats gently in place", 
            "adjusts its virtual interface",
            "glances at the user"
        ]
        action = random.choice(actions)
        current_emotion = self.emotion_engine.get_emotion() if self.emotion_engine else "neutral"
        print(f"[PersistentAvatar] (State: {self.state}, Emotion: {current_emotion}) Avatar {action}.")
        self.last_action_time = time.time()

    def _scan_surroundings(self):
        # Interact with the real world via SpatialMapper
        if self.ar_manager and self.ar_manager.spatial_mapper:
            anchors = self.ar_manager.spatial_mapper.anchors
            # Randomly decide to interact with a known spatial anchor
            if anchors and random.random() < 0.05: # 5% chance per tick
                self.state = "OBSERVING"
                anchor_id = random.choice(list(anchors.keys()))
                coords = anchors[anchor_id]
                print(f"[PersistentAvatar] Avatar notices anchor '{anchor_id}' at {coords} and moves to investigate.")
                
                # Update emotion based on "discovery"
                if self.emotion_engine:
                    self.emotion_engine.update_emotion("summon knowledge")
                
                time.sleep(3) # Simulate investigation time
                print(f"[PersistentAvatar] Avatar finished investigating '{anchor_id}'.")
                self.state = "IDLE"
                self.last_action_time = time.time()

    def interact(self, object_id):
        self.state = "INTERACTING"
        print(f"[PersistentAvatar] Avatar approaches {object_id}...")
        if self.emotion_engine:
            self.emotion_engine.update_emotion("focused")
        # Logic to interact
        time.sleep(2)
        self.state = "IDLE"
