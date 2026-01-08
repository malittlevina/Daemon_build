import threading
import time
from typing import List

# Import sensors
from sensors.vision import VisionSensor
from sensors.audio_environment import AudioEnvironmentSensor
from cognitive.peripheral_attention import PeripheralAttention

class SensorManager:
    def __init__(self, curiosity_module=None):
        self.curiosity = curiosity_module
        self.peripheral = PeripheralAttention(curiosity_module)
        self.running = False
        self.sensors = []
        
        # Initialize Vision
        self.vision = VisionSensor(use_vlm=False) # Disable VLM for speed in demo
        if self.vision.check_availability():
            self.sensors.append(self.vision)
            print("[SensorManager] Vision Sensor detected.")
        else:
            print("[SensorManager] No Vision Sensor detected (Webcam).")
            
        # Initialize Audio Environment
        self.audio = AudioEnvironmentSensor()
        self.sensors.append(self.audio)
        print("[SensorManager] Audio Environment Sensor active.")

    def start_background_loop(self):
        self.running = True
        self.audio.start()
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("[SensorManager] Background observation loop started.")

    def _loop(self):
        step = 0
        while self.running:
            try:
                step += 1
                
                # 1. Poll Vision (Interleaved modes)
                if self.vision:
                    # Every 5th check, do a peripheral scan instead of standard
                    mode = "peripheral" if step % 5 == 0 else "standard"
                    observation = self.vision.capture_and_describe(mode=mode)
                    if observation:
                        # If peripheral, route through attention module
                        if mode == "peripheral":
                            self.peripheral.process_environmental_event("Vision", observation)
                        else:
                            self._process_observation("Visual", observation)
                
                # 2. Poll Audio (Always background)
                audio_event = self.audio.check()
                if audio_event:
                    # Audio is almost always peripheral unless user is speaking (VoiceListener handles that)
                    self.peripheral.process_environmental_event("Audio", audio_event)
                
                time.sleep(2) # Frequency of observation
            except Exception as e:
                print(f"[SensorManager] Loop Error: {e}")
                time.sleep(5)

    def update_user_focus(self, focus_object):
        """Pass XR gaze data to the attention module"""
        self.peripheral.update_user_focus(focus_object)

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
