import cv2
import time
import subprocess
import base64
import os

class VisionSensor:
    def __init__(self, use_vlm=True):
        self.use_vlm = use_vlm
        self.camera_index = 0
        self.last_capture_time = 0
        self.capture_interval = 10 # Seconds between visual observations

    def capture_and_describe(self, mode="standard"):
        """
        Captures an image and returns a text description.
        Modes:
        - standard: General description
        - peripheral: Focus on background/unattended details
        """
        current_time = time.time()
        if current_time - self.last_capture_time < self.capture_interval:
            return None

        try:
            # Open camera temporarily to release resource after use
            # In a real deployed daemon, we might keep it open if latency is key
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                return None
                
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            self.last_capture_time = current_time
            
            # Simple heuristic description (Brightness/Movement)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = gray.mean()
            basic_desc = "Dark scene" if avg_brightness < 50 else "Bright scene"
            
            # VLM Integration (Ollama LLaVA)
            vlm_desc = None
            if self.use_vlm:
                prompt = "Describe this image in one short sentence."
                if mode == "peripheral":
                    prompt = "Describe background details or objects in the periphery that are not the main focus."
                vlm_desc = self._analyze_with_vlm(frame, prompt)
                
            final_desc = vlm_desc if vlm_desc else f"{basic_desc} (Camera active)"
            
            if mode == "peripheral":
                return f"[Peripheral] {final_desc}"
            return final_desc

        except Exception as e:
            # print(f"[VisionSensor] Error: {e}")
            return None

    def _analyze_with_vlm(self, frame, prompt):
        """
        Encodes frame and sends to local VLM (e.g., Ollama:llava)
        """
        try:
            # Save temp frame
            temp_path = "sensors/temp_view.jpg"
            os.makedirs("sensors", exist_ok=True)
            cv2.imwrite(temp_path, frame)
            
            # Mock VLM Response for this environment since we don't have GPU/Ollama active
            # In production: Use `ollama run llava "prompt" image.jpg` via subprocess/API
            return None 

        except Exception as e:
            print(f"[VisionSensor] VLM Error: {e}")
            return None

    def check_availability(self):
        cap = cv2.VideoCapture(self.camera_index)
        available = cap.isOpened()
        cap.release()
        return available
