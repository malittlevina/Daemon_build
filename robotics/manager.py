
from .movement import MovementController
from .hardware_interface import HardwareInterface
from .behaviors.follow import FollowBehavior

class RoboticsManager:
    def __init__(self, unimind_instance=None, vision_sensor=None):
        self.hardware = HardwareInterface()
        self.movement = MovementController(self.hardware)
        self.unimind = unimind_instance
        self.vision_sensor = vision_sensor
        self.active_behaviors = {}
        self.state = {
            "mode": "idle", # idle, follow, explore
            "battery": 100
        }
        
        if self.vision_sensor:
            self.active_behaviors["follow"] = FollowBehavior(self.movement, self.vision_sensor)

    def initialize(self):
        print("[RoboticsManager] Initializing robotics subsystem...")
        if self.hardware.connect():
            print("[RoboticsManager] Hardware connected.")
        else:
            print("[RoboticsManager] Hardware connection simulated/failed.")
    
    def set_mode(self, mode):
        print(f"[RoboticsManager] Switching mode to: {mode}")
        self.state["mode"] = mode
        
        # Deactivate all behaviors first
        for behavior in self.active_behaviors.values():
            behavior.stop()
            
        if mode == "follow" and "follow" in self.active_behaviors:
            self.active_behaviors["follow"].start()

    def update(self):
        """Called by the main daemon loop or Unimind reflection"""
        if self.state["mode"] == "follow" and "follow" in self.active_behaviors:
            self.active_behaviors["follow"].tick()

    def get_status(self):
        return self.state
