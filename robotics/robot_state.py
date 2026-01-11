# robotics/robot_state.py
"""
Robot State Manager - Symbolic state management for the companion robot.

Integrates with the daemon's symbolic state system (lam/symbolic_state.py)
to provide contextual awareness between the robot and daemon subsystems.

Tracks:
- Physical state (position, orientation, battery)
- Behavioral state (mode, current task)
- Environmental awareness (obstacles, user proximity)
- Command history and outcomes
"""

import time
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class ProximityZone(Enum):
    """User proximity zones for companion behavior."""
    CONTACT = "contact"      # Touching/perched on user
    NEAR = "near"            # Within arm's reach (< 1m)
    MEDIUM = "medium"        # Visible range (1-3m)
    FAR = "far"              # Out of immediate range (> 3m)
    UNKNOWN = "unknown"


class BatteryState(Enum):
    """Battery state levels."""
    FULL = "full"            # > 80%
    GOOD = "good"            # 40-80%
    LOW = "low"              # 15-40%
    CRITICAL = "critical"    # < 15%
    CHARGING = "charging"


@dataclass
class PhysicalState:
    """Physical state of the robot."""
    position_x: float = 0.0
    position_y: float = 0.0
    orientation: float = 0.0  # radians
    velocity_linear: float = 0.0
    velocity_angular: float = 0.0
    battery_percent: float = 100.0
    battery_state: str = "full"
    temperature: float = 25.0
    is_moving: bool = False
    is_gripping: bool = False
    grip_force: float = 0.0


@dataclass
class BehavioralState:
    """Behavioral/mental state of the robot."""
    mode: str = "idle"
    current_task: Optional[str] = None
    task_progress: float = 0.0
    last_command: Optional[str] = None
    last_command_time: float = 0.0
    attention_target: Optional[str] = None
    emotional_state: str = "neutral"  # Links to emotion engine


@dataclass
class EnvironmentalState:
    """Environmental awareness."""
    user_proximity: str = "unknown"
    user_direction: Optional[float] = None  # radians
    obstacle_front: float = 10.0
    obstacle_left: float = 10.0
    obstacle_right: float = 10.0
    environment_type: str = "unknown"  # indoor/outdoor
    lighting_level: str = "normal"
    surface_type: str = "unknown"


@dataclass
class CommandRecord:
    """Record of a command execution."""
    command: str
    params: Dict[str, Any]
    result: Dict[str, Any]
    timestamp: float
    success: bool


class RobotState:
    """
    Central state manager for the companion robot.
    
    Maintains symbolic state that can be queried by other daemon
    subsystems (LAM planner, scroll engine, NLU, etc.)
    """
    
    STATE_FILE = "config/robot_state.json"
    COMMAND_HISTORY_SIZE = 100
    
    def __init__(self):
        """Initialize robot state manager."""
        self.physical = PhysicalState()
        self.behavioral = BehavioralState()
        self.environmental = EnvironmentalState()
        
        # Command history
        self.command_history: List[CommandRecord] = []
        
        # State change callbacks
        self._callbacks: List[callable] = []
        
        # Symbolic flags for daemon integration
        self.flags: Dict[str, Any] = {
            "is_operational": False,
            "needs_charging": False,
            "user_following": False,
            "is_perched": False,
            "has_obstacle": False,
            "gesture_playing": False
        }
        
        # Context for LAM integration
        self.context: Dict[str, Any] = {
            "last_interaction": None,
            "session_start": time.time(),
            "total_distance_traveled": 0.0,
            "commands_executed": 0
        }
        
        self._load_state()
        print("[RobotState] State manager initialized")
    
    def _load_state(self) -> None:
        """Load persisted state from file."""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.context.update(data.get("context", {}))
                    self.flags.update(data.get("flags", {}))
                print("[RobotState] Loaded persisted state")
            except Exception as e:
                print(f"[RobotState] Failed to load state: {e}")
    
    def save_state(self) -> None:
        """Persist state to file."""
        os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
        try:
            data = {
                "context": self.context,
                "flags": self.flags,
                "timestamp": time.time()
            }
            with open(self.STATE_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[RobotState] Failed to save state: {e}")
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a state value.
        
        Args:
            key: State key (can use dot notation for nested values)
            value: Value to set
        """
        parts = key.split(".")
        
        if parts[0] == "physical":
            if len(parts) > 1 and hasattr(self.physical, parts[1]):
                setattr(self.physical, parts[1], value)
        elif parts[0] == "behavioral":
            if len(parts) > 1 and hasattr(self.behavioral, parts[1]):
                setattr(self.behavioral, parts[1], value)
        elif parts[0] == "environmental":
            if len(parts) > 1 and hasattr(self.environmental, parts[1]):
                setattr(self.environmental, parts[1], value)
        elif parts[0] == "flags":
            if len(parts) > 1:
                self.flags[parts[1]] = value
        elif parts[0] == "context":
            if len(parts) > 1:
                self.context[parts[1]] = value
        elif key == "mode":
            self.behavioral.mode = value
            self._update_mode_flags(value)
        else:
            # Try direct behavioral state
            if hasattr(self.behavioral, key):
                setattr(self.behavioral, key, value)
        
        self._notify_change(key, value)
    
    def get(self, key: str) -> Any:
        """
        Get a state value.
        
        Args:
            key: State key (can use dot notation)
            
        Returns:
            State value or None
        """
        parts = key.split(".")
        
        if parts[0] == "physical":
            if len(parts) > 1:
                return getattr(self.physical, parts[1], None)
            return asdict(self.physical)
        elif parts[0] == "behavioral":
            if len(parts) > 1:
                return getattr(self.behavioral, parts[1], None)
            return asdict(self.behavioral)
        elif parts[0] == "environmental":
            if len(parts) > 1:
                return getattr(self.environmental, parts[1], None)
            return asdict(self.environmental)
        elif parts[0] == "flags":
            if len(parts) > 1:
                return self.flags.get(parts[1])
            return self.flags.copy()
        elif parts[0] == "context":
            if len(parts) > 1:
                return self.context.get(parts[1])
            return self.context.copy()
        elif key == "mode":
            return self.behavioral.mode
        else:
            return getattr(self.behavioral, key, None)
    
    def get_all(self) -> Dict[str, Any]:
        """Get complete state snapshot."""
        return {
            "physical": asdict(self.physical),
            "behavioral": asdict(self.behavioral),
            "environmental": asdict(self.environmental),
            "flags": self.flags.copy(),
            "context": self.context.copy()
        }
    
    def _update_mode_flags(self, mode: str) -> None:
        """Update flags based on mode change."""
        self.flags["user_following"] = mode == "following"
        self.flags["is_perched"] = mode == "perched"
        self.flags["is_operational"] = mode not in ["emergency_stop", "simulation"]
    
    def update_from_sensors(self, sensor_data: Dict[str, Any]) -> None:
        """
        Update state from sensor readings.
        
        Args:
            sensor_data: Dictionary of sensor readings from HAL
        """
        # Update battery
        if "battery" in sensor_data:
            battery = sensor_data["battery"]["value"]
            if battery:
                self.physical.battery_percent = battery.get("percent", 100)
                self._update_battery_state()
        
        # Update distance sensors
        if "distance_front" in sensor_data:
            self.environmental.obstacle_front = sensor_data["distance_front"]["value"]
        if "distance_left" in sensor_data:
            self.environmental.obstacle_left = sensor_data["distance_left"]["value"]
        if "distance_right" in sensor_data:
            self.environmental.obstacle_right = sensor_data["distance_right"]["value"]
        
        # Update obstacle flag
        min_dist = min(
            self.environmental.obstacle_front,
            self.environmental.obstacle_left,
            self.environmental.obstacle_right
        )
        self.flags["has_obstacle"] = min_dist < 0.3  # 30cm threshold
        
        # Update grip state
        if "grip_force_left" in sensor_data and "grip_force_right" in sensor_data:
            left_force = sensor_data["grip_force_left"]["value"]
            right_force = sensor_data["grip_force_right"]["value"]
            self.physical.grip_force = (left_force + right_force) / 2
            self.physical.is_gripping = self.physical.grip_force > 0.5
    
    def _update_battery_state(self) -> None:
        """Update battery state enum based on percentage."""
        percent = self.physical.battery_percent
        if percent > 80:
            self.physical.battery_state = BatteryState.FULL.value
            self.flags["needs_charging"] = False
        elif percent > 40:
            self.physical.battery_state = BatteryState.GOOD.value
            self.flags["needs_charging"] = False
        elif percent > 15:
            self.physical.battery_state = BatteryState.LOW.value
            self.flags["needs_charging"] = True
        else:
            self.physical.battery_state = BatteryState.CRITICAL.value
            self.flags["needs_charging"] = True
    
    def update_motion_state(self, pose, velocity) -> None:
        """
        Update state from motion controller.
        
        Args:
            pose: Pose2D object
            velocity: Velocity2D object
        """
        # Track distance traveled
        dx = pose.x - self.physical.position_x
        dy = pose.y - self.physical.position_y
        distance = (dx**2 + dy**2)**0.5
        self.context["total_distance_traveled"] += distance
        
        # Update physical state
        self.physical.position_x = pose.x
        self.physical.position_y = pose.y
        self.physical.orientation = pose.theta
        self.physical.velocity_linear = velocity.linear
        self.physical.velocity_angular = velocity.angular
        self.physical.is_moving = abs(velocity.linear) > 0.01 or abs(velocity.angular) > 0.01
    
    def log_command(self, command: str, params: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Log a command execution.
        
        Args:
            command: Command name
            params: Command parameters
            result: Command result
        """
        record = CommandRecord(
            command=command,
            params=params,
            result=result,
            timestamp=time.time(),
            success=result.get("success", False)
        )
        
        self.command_history.append(record)
        if len(self.command_history) > self.COMMAND_HISTORY_SIZE:
            self.command_history = self.command_history[-self.COMMAND_HISTORY_SIZE:]
        
        self.behavioral.last_command = command
        self.behavioral.last_command_time = record.timestamp
        self.context["commands_executed"] += 1
        self.context["last_interaction"] = time.time()
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history."""
        return [
            {
                "command": r.command,
                "params": r.params,
                "success": r.success,
                "timestamp": r.timestamp
            }
            for r in self.command_history[-limit:]
        ]
    
    def update_user_proximity(self, distance: float, direction: Optional[float] = None) -> None:
        """
        Update user proximity state.
        
        Args:
            distance: Distance to user in meters
            direction: Direction to user in radians (optional)
        """
        if distance < 0.2:
            self.environmental.user_proximity = ProximityZone.CONTACT.value
        elif distance < 1.0:
            self.environmental.user_proximity = ProximityZone.NEAR.value
        elif distance < 3.0:
            self.environmental.user_proximity = ProximityZone.MEDIUM.value
        else:
            self.environmental.user_proximity = ProximityZone.FAR.value
        
        self.environmental.user_direction = direction
    
    def register_callback(self, callback: callable) -> None:
        """Register a callback for state changes."""
        self._callbacks.append(callback)
    
    def _notify_change(self, key: str, value: Any) -> None:
        """Notify callbacks of state change."""
        for callback in self._callbacks:
            try:
                callback(key, value)
            except Exception as e:
                print(f"[RobotState] Callback error: {e}")
    
    def get_symbolic_state(self) -> Dict[str, Any]:
        """
        Get symbolic state for LAM/symbolic reasoning integration.
        
        Returns:
            Dictionary compatible with lam/symbolic_state.py format
        """
        return {
            "history": [r.command for r in self.command_history[-10:]],
            "current_context": {
                "mode": self.behavioral.mode,
                "task": self.behavioral.current_task,
                "proximity": self.environmental.user_proximity,
                "battery": self.physical.battery_state,
                "moving": self.physical.is_moving
            },
            "flags": self.flags.copy()
        }
    
    def to_natural_language(self) -> str:
        """
        Generate natural language description of robot state.
        
        Returns:
            Human-readable state description
        """
        mode = self.behavioral.mode
        battery = int(self.physical.battery_percent)
        proximity = self.environmental.user_proximity
        
        parts = []
        
        # Mode description
        mode_descriptions = {
            "idle": "I am idle and ready for commands",
            "following": "I am following you",
            "perched": "I am perched on you",
            "navigating": "I am navigating to a destination",
            "simulation": "I am running in simulation mode"
        }
        parts.append(mode_descriptions.get(mode, f"I am in {mode} mode"))
        
        # Battery
        if battery < 20:
            parts.append(f"My battery is critical at {battery}%")
        elif battery < 50:
            parts.append(f"My battery is at {battery}%")
        
        # Proximity
        if proximity == "contact":
            parts.append("I am attached to you")
        elif proximity == "near":
            parts.append("You are nearby")
        elif proximity == "far":
            parts.append("You are far from me")
        
        # Obstacles
        if self.flags.get("has_obstacle"):
            parts.append("I detect an obstacle nearby")
        
        return ". ".join(parts) + "."
