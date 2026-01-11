
from .hardware_interface import HardwareInterface

class MovementController:
    def __init__(self, hardware: HardwareInterface):
        self.hardware = hardware
        self.current_vector = (0, 0, 0) # x, y, rotation

    def move(self, x, y, speed=1.0):
        self.current_vector = (x, y, 0)
        self.hardware.send_command("motors", "move_vector", {"x": x, "y": y, "speed": speed})

    def rotate(self, angle, speed=1.0):
        self.current_vector = (0, 0, angle)
        self.hardware.send_command("motors", "rotate", {"angle": angle, "speed": speed})

    def stop(self):
        self.current_vector = (0, 0, 0)
        self.hardware.send_command("motors", "stop")
