from __future__ import annotations

try:
    import cv2  # type: ignore
except Exception as e:  # pragma: no cover
    cv2 = None
    _CV2_IMPORT_ERROR = e

class VisionSensor:
    def __init__(self, model_path="sensors/yolo_model.onnx"):
        if cv2 is None:
            raise RuntimeError(f"OpenCV unavailable: {_CV2_IMPORT_ERROR}")
        self.model_path = model_path
        self.capture = cv2.VideoCapture(0)

    def classify_scene(self):
        ret, frame = self.capture.read()
        if not ret:
            return "No camera input"
        # Stub for model-based scene detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = gray.mean()
        return "Indoor" if avg_brightness < 100 else "Outdoor"

    def classify_surroundings(self):
        scene = self.classify_scene()
        print(f"[VisionSensor] Surroundings classified as: {scene}")
        return scene

    def release(self):
        self.capture.release()
