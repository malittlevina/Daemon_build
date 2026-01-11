
class FollowBehavior:
    def __init__(self, movement_controller, vision_sensor):
        self.movement = movement_controller
        self.vision = vision_sensor
        self.active = False
        self.target_locked = False

    def tick(self):
        if not self.active:
            return

        # Use the vision sensor to find a target (stub logic)
        # In a real scenario, we would get bounding boxes or depth info
        scene_info = self.vision.classify_surroundings()
        
        # Simple simulation: if "Outdoor", move forward. If "Indoor", stop (safety).
        # This is a placeholder for actual "follow" logic which would rely on object detection.
        # We will assume a "target_detected" property on the vision sensor for this thought experiment.
        
        # Mocking target detection logic
        target_distance = 2.0 # meters, ideal distance
        current_distance = 3.0 # simulated reading
        
        if scene_info:
            # Simple P-controller logic (stub)
            error = current_distance - target_distance
            if error > 0.5:
                print("[FollowBehavior] Target far. Moving closer.")
                self.movement.move(1, 0, speed=0.5)
            elif error < -0.5:
                print("[FollowBehavior] Target too close. Backing up.")
                self.movement.move(-1, 0, speed=0.5)
            else:
                self.movement.stop()

    def start(self):
        self.active = True
        print("[FollowBehavior] Started.")

    def stop(self):
        self.active = False
        self.movement.stop()
        print("[FollowBehavior] Stopped.")
