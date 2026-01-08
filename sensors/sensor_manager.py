import threading
import time
from typing import List

# Import sensors
from sensors.vision import VisionSensor
# from sensors.audio import AudioSensor (Assuming we refactor audio similarly)

class SensorManager:
    def __init__(self, curiosity_module=None):
        self.curiosity = curiosity_module
        self.running = False
        self.sensors = []
        
        # Initialize Vision
        self.vision = VisionSensor(use_vlm=False) # Disable VLM for speed in demo
        if self.vision.check_availability():
            self.sensors.append(self.vision)
            print("[SensorManager] Vision Sensor detected.")
        else:
            print("[SensorManager] No Vision Sensor detected (Webcam).")

    def start_background_loop(self):
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("[SensorManager] Background observation loop started.")

    def _loop(self):
        while self.running:
            try:
                # Poll Vision
                if self.vision:
                    observation = self.vision.capture_and_describe()
                    if observation:
                        self._process_observation("Visual", observation)
                
                # Poll other sensors...
                
                time.sleep(1) # Frequency of observation
            except Exception as e:
                print(f"[SensorManager] Loop Error: {e}")
                time.sleep(5)

    def _process_observation(self, sensor_type, content):
        # Log basic observation
        # print(f"[{sensor_type} Observation] {content}")
        
        # Feed to Curiosity Module
        if self.curiosity:
            context = "RealWorld"
            event = f"{sensor_type}Input"
            outcome = content
            
            is_interesting = self.curiosity.process_observation(context, event, outcome)
            if is_interesting:
                 print(f"[SensorManager] 💡 Interesting Real-World Observation: {content}")

    def stop(self):
        self.running = False
