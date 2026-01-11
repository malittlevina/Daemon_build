# robotics/robot_core.py
"""
Robot Core - Central orchestrator for all robotics subsystems.

This is the main entry point for robotics control, coordinating:
- Hardware abstraction
- Motion control
- State management
- Navigation
- Companion behaviors
"""

import threading
import time
from typing import Optional, Dict, Any, Callable
from enum import Enum


class RobotMode(Enum):
    """Operating modes for the companion robot."""
    IDLE = "idle"
    FOLLOWING = "following"
    PERCHED = "perched"
    NAVIGATING = "navigating"
    DOCKED = "docked"
    EMERGENCY_STOP = "emergency_stop"
    SIMULATION = "simulation"


class RobotCore:
    """
    Central orchestrator for the companion robot.
    
    Manages all robotics subsystems and provides a unified interface
    for the daemon to control robot behavior.
    """
    
    def __init__(self, simulation_mode: bool = True):
        """
        Initialize the robot core.
        
        Args:
            simulation_mode: If True, run without real hardware (for development)
        """
        self.simulation_mode = simulation_mode
        self.mode = RobotMode.SIMULATION if simulation_mode else RobotMode.IDLE
        self._running = False
        self._control_thread: Optional[threading.Thread] = None
        self._callbacks: Dict[str, list] = {
            "mode_change": [],
            "error": [],
            "status_update": []
        }
        
        # Subsystem references (lazy-loaded)
        self._hal = None
        self._motion = None
        self._state = None
        self._navigation = None
        self._companion = None
        
        # Control loop timing
        self.control_rate_hz = 50  # 50Hz control loop
        self.last_update_time = 0.0
        
        print(f"[RobotCore] Initialized in {'simulation' if simulation_mode else 'hardware'} mode")
    
    @property
    def hal(self):
        """Lazy-load Hardware Abstraction Layer."""
        if self._hal is None:
            from robotics.hal import HardwareAbstractionLayer
            self._hal = HardwareAbstractionLayer(simulation=self.simulation_mode)
        return self._hal
    
    @property
    def motion(self):
        """Lazy-load Motion Controller."""
        if self._motion is None:
            from robotics.motion_controller import MotionController
            self._motion = MotionController(self.hal)
        return self._motion
    
    @property
    def state(self):
        """Lazy-load Robot State Manager."""
        if self._state is None:
            from robotics.robot_state import RobotState
            self._state = RobotState()
        return self._state
    
    @property
    def navigation(self):
        """Lazy-load Navigation Planner."""
        if self._navigation is None:
            from robotics.navigation import NavigationPlanner
            self._navigation = NavigationPlanner(self.motion, self.state)
        return self._navigation
    
    @property
    def companion(self):
        """Lazy-load Companion Behaviors."""
        if self._companion is None:
            from robotics.companion import CompanionBehaviors
            self._companion = CompanionBehaviors(self)
        return self._companion
    
    def start(self) -> bool:
        """
        Start the robot control loop.
        
        Returns:
            True if started successfully
        """
        if self._running:
            print("[RobotCore] Already running")
            return False
        
        try:
            # Initialize hardware
            if not self.hal.initialize():
                raise RuntimeError("Failed to initialize hardware")
            
            # Start control thread
            self._running = True
            self._control_thread = threading.Thread(
                target=self._control_loop,
                daemon=True,
                name="RobotControlLoop"
            )
            self._control_thread.start()
            
            self.set_mode(RobotMode.IDLE)
            print("[RobotCore] Robot control started")
            return True
            
        except Exception as e:
            self._running = False
            self._trigger_callback("error", {"message": str(e)})
            print(f"[RobotCore] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the robot control loop safely.
        
        Returns:
            True if stopped successfully
        """
        if not self._running:
            return True
        
        print("[RobotCore] Stopping robot control...")
        self._running = False
        
        # Emergency stop all motion
        self.motion.emergency_stop()
        
        if self._control_thread:
            self._control_thread.join(timeout=2.0)
        
        # Shutdown hardware
        self.hal.shutdown()
        
        self.set_mode(RobotMode.IDLE)
        print("[RobotCore] Robot control stopped")
        return True
    
    def set_mode(self, mode: RobotMode) -> None:
        """
        Set the robot operating mode.
        
        Args:
            mode: The new operating mode
        """
        old_mode = self.mode
        self.mode = mode
        self.state.set("mode", mode.value)
        self._trigger_callback("mode_change", {
            "old_mode": old_mode.value,
            "new_mode": mode.value
        })
        print(f"[RobotCore] Mode changed: {old_mode.value} -> {mode.value}")
    
    def _control_loop(self) -> None:
        """
        Main control loop running at fixed rate.
        Handles sensor reading, state updates, and motor commands.
        """
        period = 1.0 / self.control_rate_hz
        
        while self._running:
            loop_start = time.time()
            
            try:
                # Update sensor readings
                self.hal.update_sensors()
                
                # Update robot state
                self.state.update_from_sensors(self.hal.get_sensor_data())
                
                # Execute current behavior based on mode
                self._execute_mode_behavior()
                
                # Update motor outputs
                self.hal.update_actuators()
                
                self.last_update_time = time.time()
                self._trigger_callback("status_update", self.get_status())
                
            except Exception as e:
                print(f"[RobotCore] Control loop error: {e}")
                self._trigger_callback("error", {"message": str(e)})
            
            # Maintain fixed loop rate
            elapsed = time.time() - loop_start
            if elapsed < period:
                time.sleep(period - elapsed)
    
    def _execute_mode_behavior(self) -> None:
        """Execute behavior based on current mode."""
        if self.mode == RobotMode.FOLLOWING:
            self.companion.follow_behavior()
        elif self.mode == RobotMode.PERCHED:
            self.companion.perched_behavior()
        elif self.mode == RobotMode.NAVIGATING:
            self.navigation.execute_step()
        elif self.mode == RobotMode.IDLE:
            self.companion.idle_behavior()
        elif self.mode == RobotMode.EMERGENCY_STOP:
            self.motion.emergency_stop()
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for robot events.
        
        Args:
            event: Event type ("mode_change", "error", "status_update")
            callback: Function to call when event occurs
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, data: Dict[str, Any]) -> None:
        """Trigger all callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"[RobotCore] Callback error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current robot status.
        
        Returns:
            Dictionary with current robot state
        """
        return {
            "mode": self.mode.value,
            "running": self._running,
            "simulation": self.simulation_mode,
            "state": self.state.get_all(),
            "last_update": self.last_update_time
        }
    
    def execute_command(self, command: str, **params) -> Dict[str, Any]:
        """
        Execute a high-level robot command.
        
        This is the main interface for the daemon to control the robot.
        
        Args:
            command: Command name
            **params: Command parameters
            
        Returns:
            Command result
        """
        command_handlers = {
            "start": lambda: {"success": self.start()},
            "stop": lambda: {"success": self.stop()},
            "follow": lambda: self._cmd_follow(**params),
            "perch": lambda: self._cmd_perch(**params),
            "navigate": lambda: self._cmd_navigate(**params),
            "status": lambda: self.get_status(),
            "calibrate": lambda: self._cmd_calibrate(),
            "gesture": lambda: self._cmd_gesture(**params),
            "idle": lambda: self._cmd_idle(),
        }
        
        handler = command_handlers.get(command)
        if handler:
            result = handler()
            self.state.log_command(command, params, result)
            return result
        else:
            return {"error": f"Unknown command: {command}"}
    
    def _cmd_follow(self, **params) -> Dict[str, Any]:
        """Start follow mode."""
        self.set_mode(RobotMode.FOLLOWING)
        distance = params.get("distance", 1.0)  # meters
        self.companion.set_follow_distance(distance)
        return {"success": True, "mode": "following", "distance": distance}
    
    def _cmd_perch(self, **params) -> Dict[str, Any]:
        """Enter perched/attached mode."""
        self.set_mode(RobotMode.PERCHED)
        location = params.get("location", "shoulder")
        self.companion.set_perch_location(location)
        return {"success": True, "mode": "perched", "location": location}
    
    def _cmd_navigate(self, **params) -> Dict[str, Any]:
        """Navigate to a target."""
        target = params.get("target")
        if not target:
            return {"error": "No target specified"}
        self.set_mode(RobotMode.NAVIGATING)
        self.navigation.set_target(target)
        return {"success": True, "mode": "navigating", "target": target}
    
    def _cmd_calibrate(self) -> Dict[str, Any]:
        """Run calibration routine."""
        self.motion.calibrate()
        return {"success": True, "message": "Calibration complete"}
    
    def _cmd_gesture(self, **params) -> Dict[str, Any]:
        """Perform a gesture."""
        gesture_name = params.get("name", "wave")
        self.companion.perform_gesture(gesture_name)
        return {"success": True, "gesture": gesture_name}
    
    def _cmd_idle(self) -> Dict[str, Any]:
        """Enter idle mode."""
        self.set_mode(RobotMode.IDLE)
        return {"success": True, "mode": "idle"}
