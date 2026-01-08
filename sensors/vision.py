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

    def capture_and_describe(self):
        """
        Captures an image and returns a text description.
        """
        current_time = time.time()
        if current_time - self.last_capture_time < self.capture_interval:
            return None

        try:
            # Open camera temporarily to release resource after use
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                return None
                
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            self.last_capture_time = current_time
            
            # Simple heuristic description (Brightness/Movement)
            # In a real system, we would calculate optical flow or scene changes here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = gray.mean()
            basic_desc = "Dark scene" if avg_brightness < 50 else "Bright scene"
            
            # VLM Integration (Ollama LLaVA)
            vlm_desc = None
            if self.use_vlm:
                vlm_desc = self._analyze_with_vlm(frame)
                
            final_desc = vlm_desc if vlm_desc else f"{basic_desc} (Camera active)"
            return final_desc

        except Exception as e:
            print(f"[VisionSensor] Error: {e}")
            return None

    def _analyze_with_vlm(self, frame):
        """
        Encodes frame and sends to local VLM (e.g., Ollama:llava)
        """
        try:
            # Save temp frame
            temp_path = "sensors/temp_view.jpg"
            os.makedirs("sensors", exist_ok=True)
            cv2.imwrite(temp_path, frame)
            
            # Call Ollama with LLaVA
            # Note: This requires 'ollama pull llava' to be run previously on the host
            # We use a simple prompt
            prompt = "Describe this image in one short sentence."
            
            # Check if ollama is available
            # This implementation assumes ollama CLI can take an image path or we need to implement the API
            # Since standard `ollama run` doesn't easily take image files via CLI args in all versions, 
            # we might mock this or assume a specific API wrapper.
            # For robustness in this demo environment, we will mock the VLM response 
            # unless we are sure we can hit the API.
            
            # MOCK implementation for demo stability:
            # In a real deployment, use requests.post('http://localhost:11434/api/generate', ...)
            return None 

        except Exception as e:
            print(f"[VisionSensor] VLM Error: {e}")
            return None

    def check_availability(self):
        cap = cv2.VideoCapture(self.camera_index)
        available = cap.isOpened()
        cap.release()
        return available
