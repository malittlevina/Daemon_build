import time
import random
import threading

class AudioEnvironmentSensor:
    def __init__(self, sensitivity=0.5):
        self.sensitivity = sensitivity
        self.active = False
        self.last_event = None
        self.known_sounds = [
            "distant_siren", "keyboard_typing", "bird_chirping", 
            "hvac_hum", "conversation_muffled", "door_closing",
            "rain_patter", "silence"
        ]

    def start(self):
        self.active = True
        # In a real implementation, this would start a PyAudio stream or YAMNet classifier
        print("[AudioEnvironment] Background listening started.")

    def stop(self):
        self.active = False

    def listen_segment(self, duration=2.0):
        """
        Simulates listening to a segment of audio and classifying the background noise.
        """
        if not self.active:
            return None

        # Simulation Logic:
        # In a real environment, we'd capture audio buffer -> FFT/Spectrogram -> Classifier
        time.sleep(duration * 0.1) # Simulate processing time
        
        # Randomly detect background events based on "sensitivity"
        if random.random() < (0.1 * self.sensitivity):
            event = random.choice(self.known_sounds)
            if event != "silence":
                return event
        
        return None

    def check(self):
        """
        Polls for a new event.
        """
        event = self.listen_segment()
        if event and event != self.last_event:
            self.last_event = event
            return f"Background Sound: {event}"
        return None
