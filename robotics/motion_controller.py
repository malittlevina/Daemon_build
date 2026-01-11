# robotics/motion_controller.py
"""
Motion Controller for Companion Robot.

Provides movement primitives and motion planning:
- Differential drive control for wheeled movement
- Servo coordination for head/arm movements
- Gesture sequences
- Grip control for perching
"""

import time
import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class MovementState(Enum):
    """State of the motion controller."""
    IDLE = "idle"
    MOVING = "moving"
    TURNING = "turning"
    GESTURE = "gesture"
    CALIBRATING = "calibrating"
    ERROR = "error"


@dataclass
class Pose2D:
    """2D pose (position and orientation)."""
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0  # radians
    
    def distance_to(self, other: 'Pose2D') -> float:
        """Calculate distance to another pose."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def angle_to(self, other: 'Pose2D') -> float:
        """Calculate angle to another pose."""
        return math.atan2(other.y - self.y, other.x - self.x)


@dataclass
class Velocity2D:
    """2D velocity (linear and angular)."""
    linear: float = 0.0  # m/s
    angular: float = 0.0  # rad/s


@dataclass
class MotionProfile:
    """Motion profile for smooth movement."""
    max_linear_velocity: float = 0.5  # m/s
    max_angular_velocity: float = 1.5  # rad/s
    linear_acceleration: float = 0.5  # m/s^2
    angular_acceleration: float = 2.0  # rad/s^2


class MotionController:
    """
    Motion controller for the companion robot.
    
    Handles:
    - Differential drive kinematics
    - Velocity profiling
    - Gesture sequences
    - Calibration routines
    """
    
    def __init__(self, hal):
        """
        Initialize motion controller.
        
        Args:
            hal: Hardware abstraction layer instance
        """
        self.hal = hal
        self.state = MovementState.IDLE
        
        # Robot parameters
        self.wheel_base = 0.15  # meters (distance between wheels)
        self.wheel_radius = 0.03  # meters
        
        # Current state
        self.pose = Pose2D()
        self.velocity = Velocity2D()
        self.target_velocity = Velocity2D()
        
        # Motion profile
        self.profile = MotionProfile()
        
        # Gesture library
        self.gestures = self._load_gesture_library()
        self._current_gesture: Optional[List[Dict]] = None
        self._gesture_step = 0
        self._gesture_start_time = 0.0
        
        print("[MotionController] Initialized")
    
    def _load_gesture_library(self) -> Dict[str, List[Dict]]:
        """Load predefined gesture sequences."""
        return {
            "wave": [
                {"arm_right": 90, "duration": 0.3},
                {"arm_right": 45, "duration": 0.2},
                {"arm_right": 90, "duration": 0.2},
                {"arm_right": 45, "duration": 0.2},
                {"arm_right": 90, "duration": 0.2},
                {"arm_right": 0, "duration": 0.3}
            ],
            "nod": [
                {"neck_tilt": 30, "duration": 0.2},
                {"neck_tilt": -10, "duration": 0.2},
                {"neck_tilt": 30, "duration": 0.2},
                {"neck_tilt": 0, "duration": 0.2}
            ],
            "shake_head": [
                {"neck_pan": 30, "duration": 0.2},
                {"neck_pan": -30, "duration": 0.3},
                {"neck_pan": 30, "duration": 0.3},
                {"neck_pan": 0, "duration": 0.2}
            ],
            "look_around": [
                {"neck_pan": -45, "neck_tilt": 10, "duration": 0.5},
                {"neck_pan": 45, "neck_tilt": -10, "duration": 0.8},
                {"neck_pan": 0, "neck_tilt": 0, "duration": 0.4}
            ],
            "happy": [
                {"arm_left": 60, "arm_right": 60, "neck_tilt": 20, "duration": 0.3},
                {"arm_left": 30, "arm_right": 30, "duration": 0.2},
                {"arm_left": 60, "arm_right": 60, "duration": 0.2},
                {"arm_left": 0, "arm_right": 0, "neck_tilt": 0, "duration": 0.3}
            ],
            "sad": [
                {"neck_tilt": -15, "arm_left": -20, "arm_right": -20, "duration": 0.5},
                {"duration": 1.0},  # Hold
                {"neck_tilt": 0, "arm_left": 0, "arm_right": 0, "duration": 0.5}
            ],
            "curious": [
                {"neck_pan": 20, "neck_tilt": 30, "duration": 0.4},
                {"duration": 0.5},
                {"neck_pan": -20, "neck_tilt": 30, "duration": 0.5},
                {"neck_pan": 0, "neck_tilt": 0, "duration": 0.3}
            ],
            "attention": [
                {"neck_tilt": 15, "duration": 0.2},
                {"duration": 0.3},
                {"neck_tilt": 0, "duration": 0.2}
            ],
            "sleep": [
                {"neck_tilt": -20, "arm_left": -30, "arm_right": -30, "duration": 1.0},
            ],
            "wake": [
                {"neck_tilt": 0, "arm_left": 0, "arm_right": 0, "duration": 0.5},
                {"neck_tilt": 20, "duration": 0.3},
                {"neck_tilt": 0, "duration": 0.2}
            ]
        }
    
    def set_velocity(self, linear: float, angular: float) -> None:
        """
        Set target velocity for differential drive.
        
        Args:
            linear: Forward velocity in m/s
            angular: Angular velocity in rad/s
        """
        # Clamp to max velocities
        linear = max(-self.profile.max_linear_velocity, 
                    min(self.profile.max_linear_velocity, linear))
        angular = max(-self.profile.max_angular_velocity,
                     min(self.profile.max_angular_velocity, angular))
        
        self.target_velocity = Velocity2D(linear, angular)
        
        if abs(linear) > 0.01 or abs(angular) > 0.01:
            self.state = MovementState.MOVING if abs(linear) > abs(angular) else MovementState.TURNING
        else:
            self.state = MovementState.IDLE
    
    def update(self, dt: float = 0.02) -> None:
        """
        Update motion controller state.
        
        Args:
            dt: Time delta since last update
        """
        # Update velocity with acceleration limits
        self._update_velocity(dt)
        
        # Convert to wheel velocities and send to HAL
        self._update_wheel_commands()
        
        # Update odometry
        self._update_odometry(dt)
        
        # Update gesture if active
        if self._current_gesture:
            self._update_gesture()
    
    def _update_velocity(self, dt: float) -> None:
        """Apply acceleration limits to velocity."""
        # Linear velocity
        linear_error = self.target_velocity.linear - self.velocity.linear
        max_linear_step = self.profile.linear_acceleration * dt
        if abs(linear_error) <= max_linear_step:
            self.velocity.linear = self.target_velocity.linear
        else:
            self.velocity.linear += math.copysign(max_linear_step, linear_error)
        
        # Angular velocity
        angular_error = self.target_velocity.angular - self.velocity.angular
        max_angular_step = self.profile.angular_acceleration * dt
        if abs(angular_error) <= max_angular_step:
            self.velocity.angular = self.target_velocity.angular
        else:
            self.velocity.angular += math.copysign(max_angular_step, angular_error)
    
    def _update_wheel_commands(self) -> None:
        """Convert body velocity to wheel velocities."""
        # Differential drive inverse kinematics
        # v_left = v - w * L/2
        # v_right = v + w * L/2
        half_base = self.wheel_base / 2.0
        
        v_left = self.velocity.linear - self.velocity.angular * half_base
        v_right = self.velocity.linear + self.velocity.angular * half_base
        
        # Normalize to motor range (-1 to 1)
        max_wheel_velocity = 0.5  # m/s
        motor_left = v_left / max_wheel_velocity
        motor_right = v_right / max_wheel_velocity
        
        # Clamp and send to HAL
        self.hal.set_motor("wheel_left", max(-1, min(1, motor_left)))
        self.hal.set_motor("wheel_right", max(-1, min(1, motor_right)))
    
    def _update_odometry(self, dt: float) -> None:
        """Update robot pose based on wheel encoders."""
        # Simple dead reckoning (would use encoders on real hardware)
        v = self.velocity.linear
        w = self.velocity.angular
        
        if abs(w) < 0.001:
            # Straight line motion
            self.pose.x += v * dt * math.cos(self.pose.theta)
            self.pose.y += v * dt * math.sin(self.pose.theta)
        else:
            # Arc motion
            r = v / w
            self.pose.x += r * (math.sin(self.pose.theta + w * dt) - math.sin(self.pose.theta))
            self.pose.y += r * (math.cos(self.pose.theta) - math.cos(self.pose.theta + w * dt))
            self.pose.theta += w * dt
        
        # Normalize theta to [-pi, pi]
        self.pose.theta = math.atan2(math.sin(self.pose.theta), math.cos(self.pose.theta))
    
    def move_forward(self, speed: float = 0.3) -> None:
        """Move forward at given speed."""
        self.set_velocity(speed, 0)
    
    def move_backward(self, speed: float = 0.3) -> None:
        """Move backward at given speed."""
        self.set_velocity(-speed, 0)
    
    def turn_left(self, speed: float = 1.0) -> None:
        """Turn left (counterclockwise)."""
        self.set_velocity(0, speed)
    
    def turn_right(self, speed: float = 1.0) -> None:
        """Turn right (clockwise)."""
        self.set_velocity(0, -speed)
    
    def stop(self) -> None:
        """Stop all movement."""
        self.set_velocity(0, 0)
    
    def emergency_stop(self) -> None:
        """Immediately stop all motors."""
        self.velocity = Velocity2D(0, 0)
        self.target_velocity = Velocity2D(0, 0)
        self.hal.emergency_stop()
        self.state = MovementState.IDLE
        self._current_gesture = None
        print("[MotionController] Emergency stop!")
    
    def look_at(self, pan: float, tilt: float) -> None:
        """
        Move head to look at a direction.
        
        Args:
            pan: Horizontal angle in degrees (-90 to 90)
            tilt: Vertical angle in degrees (-30 to 60)
        """
        self.hal.set_motor("neck_pan", pan)
        self.hal.set_motor("neck_tilt", tilt)
    
    def set_grip(self, force: float) -> None:
        """
        Set grip force for perching.
        
        Args:
            force: Grip force (0 = open, 1 = max grip)
        """
        # Convert force to grip angle
        grip_angle = 45 + force * 45  # 45° open, 90° closed
        self.hal.set_motor("grip_left", grip_angle)
        self.hal.set_motor("grip_right", grip_angle)
    
    def start_gesture(self, gesture_name: str) -> bool:
        """
        Start a predefined gesture.
        
        Args:
            gesture_name: Name of gesture from library
            
        Returns:
            True if gesture started
        """
        if gesture_name not in self.gestures:
            print(f"[MotionController] Unknown gesture: {gesture_name}")
            return False
        
        self._current_gesture = self.gestures[gesture_name]
        self._gesture_step = 0
        self._gesture_start_time = time.time()
        self.state = MovementState.GESTURE
        print(f"[MotionController] Starting gesture: {gesture_name}")
        return True
    
    def _update_gesture(self) -> None:
        """Update gesture playback."""
        if not self._current_gesture:
            return
        
        if self._gesture_step >= len(self._current_gesture):
            # Gesture complete
            self._current_gesture = None
            self.state = MovementState.IDLE
            print("[MotionController] Gesture complete")
            return
        
        step = self._current_gesture[self._gesture_step]
        elapsed = time.time() - self._gesture_start_time
        
        # Apply motor commands from step
        for key, value in step.items():
            if key != "duration" and key in ["arm_left", "arm_right", "neck_pan", "neck_tilt"]:
                self.hal.set_motor(key, value)
        
        # Check if step duration elapsed
        duration = step.get("duration", 0.5)
        if elapsed >= duration:
            self._gesture_step += 1
            self._gesture_start_time = time.time()
    
    def is_gesture_active(self) -> bool:
        """Check if a gesture is currently playing."""
        return self._current_gesture is not None
    
    def calibrate(self) -> bool:
        """
        Run calibration routine.
        
        Returns:
            True if calibration successful
        """
        self.state = MovementState.CALIBRATING
        print("[MotionController] Starting calibration...")
        
        # Home all motors
        self.hal.home_all_motors()
        time.sleep(1.0)
        
        # Reset odometry
        self.pose = Pose2D()
        self.velocity = Velocity2D()
        self.target_velocity = Velocity2D()
        
        self.state = MovementState.IDLE
        print("[MotionController] Calibration complete")
        return True
    
    def get_pose(self) -> Pose2D:
        """Get current robot pose."""
        return self.pose
    
    def set_pose(self, pose: Pose2D) -> None:
        """Set robot pose (for localization updates)."""
        self.pose = pose
    
    def get_velocity(self) -> Velocity2D:
        """Get current velocity."""
        return self.velocity
    
    def get_state(self) -> Dict[str, Any]:
        """Get motion controller state."""
        return {
            "state": self.state.value,
            "pose": {"x": self.pose.x, "y": self.pose.y, "theta": self.pose.theta},
            "velocity": {"linear": self.velocity.linear, "angular": self.velocity.angular},
            "target_velocity": {
                "linear": self.target_velocity.linear,
                "angular": self.target_velocity.angular
            },
            "gesture_active": self.is_gesture_active()
        }
    
    def drive_to_pose(self, target: Pose2D, tolerance: float = 0.1) -> bool:
        """
        Simple drive-to-pose controller.
        
        Args:
            target: Target pose
            tolerance: Position tolerance in meters
            
        Returns:
            True if reached target
        """
        distance = self.pose.distance_to(target)
        
        if distance < tolerance:
            self.stop()
            return True
        
        # Calculate angle to target
        angle_to_target = self.pose.angle_to(target)
        angle_error = angle_to_target - self.pose.theta
        
        # Normalize angle error
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi
        
        # Turn first, then drive
        if abs(angle_error) > 0.2:  # ~11 degrees
            angular_velocity = 0.8 * angle_error
            angular_velocity = max(-1.0, min(1.0, angular_velocity))
            self.set_velocity(0, angular_velocity)
        else:
            # Drive toward target
            linear_velocity = min(0.3, 0.5 * distance)
            angular_velocity = 0.5 * angle_error
            self.set_velocity(linear_velocity, angular_velocity)
        
        return False
