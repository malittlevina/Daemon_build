# scrolls/robot_scrolls.py
"""
Robot Control Scrolls for the Daemon.

Provides scroll actions for robotics control, allowing the daemon
to issue robot commands through the scroll engine.

These scrolls integrate with:
- ScrollEngine for action invocation
- NLU for intent recognition
- LAM for symbolic planning
"""

from typing import Dict, Any, Optional
from scrolls.scroll_action import ScrollAction


class RobotScrolls:
    """
    Collection of robot control scroll actions.
    
    Scroll naming convention: robot_<action>
    """
    
    _robot_core = None
    
    @classmethod
    def get_robot(cls):
        """Get or create RobotCore singleton."""
        if cls._robot_core is None:
            try:
                from robotics.robot_core import RobotCore
                cls._robot_core = RobotCore(simulation_mode=True)
                print("[RobotScrolls] RobotCore initialized")
            except Exception as e:
                print(f"[RobotScrolls] Failed to initialize RobotCore: {e}")
        return cls._robot_core
    
    @classmethod
    def initialize_robot(cls, simulation: bool = True) -> Dict[str, Any]:
        """
        Initialize the robot system.
        
        Args:
            simulation: Run in simulation mode
            
        Returns:
            Result dictionary
        """
        try:
            from robotics.robot_core import RobotCore
            cls._robot_core = RobotCore(simulation_mode=simulation)
            success = cls._robot_core.start()
            return {
                "success": success,
                "message": "Robot initialized" if success else "Failed to start robot",
                "simulation": simulation
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @classmethod
    def shutdown_robot(cls) -> Dict[str, Any]:
        """Shutdown the robot safely."""
        if cls._robot_core:
            cls._robot_core.stop()
            return {"success": True, "message": "Robot shutdown complete"}
        return {"success": False, "message": "Robot not running"}
    
    @classmethod
    def robot_follow(cls, distance: float = 1.0) -> Dict[str, Any]:
        """
        Start following the user.
        
        Args:
            distance: Following distance in meters
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        return robot.execute_command("follow", distance=distance)
    
    @classmethod
    def robot_stop(cls) -> Dict[str, Any]:
        """Stop all robot movement."""
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        return robot.execute_command("idle")
    
    @classmethod
    def robot_perch(cls, location: str = "shoulder") -> Dict[str, Any]:
        """
        Enter perched mode on user.
        
        Args:
            location: Where to perch (shoulder, arm, pocket)
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        return robot.execute_command("perch", location=location)
    
    @classmethod
    def robot_navigate(cls, target: str) -> Dict[str, Any]:
        """
        Navigate to a target location.
        
        Args:
            target: Destination (semantic name or "x,y" coordinates)
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        return robot.execute_command("navigate", target=target)
    
    @classmethod
    def robot_gesture(cls, gesture_name: str = "wave") -> Dict[str, Any]:
        """
        Perform a gesture.
        
        Args:
            gesture_name: Name of gesture (wave, nod, happy, etc.)
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        return robot.execute_command("gesture", name=gesture_name)
    
    @classmethod
    def robot_status(cls) -> Dict[str, Any]:
        """Get current robot status."""
        robot = cls.get_robot()
        if not robot:
            return {
                "success": False, 
                "error": "Robot not available",
                "running": False
            }
        
        return robot.execute_command("status")
    
    @classmethod
    def robot_calibrate(cls) -> Dict[str, Any]:
        """Run robot calibration routine."""
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        return robot.execute_command("calibrate")
    
    @classmethod
    def robot_look_at(cls, pan: float = 0, tilt: float = 0) -> Dict[str, Any]:
        """
        Point robot head in a direction.
        
        Args:
            pan: Horizontal angle (-90 to 90 degrees)
            tilt: Vertical angle (-30 to 60 degrees)
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        robot.motion.look_at(pan, tilt)
        return {"success": True, "pan": pan, "tilt": tilt}
    
    @classmethod
    def robot_learn_location(cls, name: str) -> Dict[str, Any]:
        """
        Learn current position as a named location.
        
        Args:
            name: Name for this location
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        pose = robot.motion.get_pose()
        robot.navigation.add_semantic_location(name, pose.x, pose.y)
        
        return {
            "success": True,
            "message": f"Learned location '{name}'",
            "position": {"x": pose.x, "y": pose.y}
        }
    
    @classmethod
    def robot_go_home(cls) -> Dict[str, Any]:
        """Navigate robot to home/charging station."""
        return cls.robot_navigate("home")
    
    @classmethod
    def robot_charge(cls) -> Dict[str, Any]:
        """Navigate to charging station and dock."""
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        # Navigate to charging station
        result = robot.execute_command("navigate", target="charging_station")
        
        # Set to docked mode when arrived
        if result.get("success"):
            from robotics.robot_core import RobotMode
            robot.set_mode(RobotMode.DOCKED)
        
        return result
    
    @classmethod
    def robot_express(cls, emotion: str) -> Dict[str, Any]:
        """
        Express an emotion through gesture.
        
        Args:
            emotion: Emotion to express (happy, sad, curious, etc.)
        """
        emotion_gestures = {
            "happy": "happy",
            "sad": "sad",
            "excited": "happy",
            "curious": "curious",
            "alert": "attention",
            "sleepy": "sleep",
            "awake": "wake",
            "greeting": "wave",
            "yes": "nod",
            "no": "shake_head"
        }
        
        gesture = emotion_gestures.get(emotion.lower(), "attention")
        return cls.robot_gesture(gesture)
    
    @classmethod
    def robot_set_personality(cls, trait: str, value: float) -> Dict[str, Any]:
        """
        Set a personality trait.
        
        Args:
            trait: Personality trait name
            value: Value 0-1
        """
        robot = cls.get_robot()
        if not robot:
            return {"success": False, "error": "Robot not available"}
        
        robot.companion.set_personality_trait(trait, value)
        return {
            "success": True,
            "trait": trait,
            "value": value
        }
    
    @classmethod
    def get_all_scrolls(cls) -> Dict[str, callable]:
        """
        Get all robot scrolls for registration with ScrollEngine.
        
        Returns:
            Dictionary of scroll name -> function
        """
        return {
            "robot start": lambda: cls.initialize_robot(),
            "robot stop": lambda: cls.shutdown_robot(),
            "robot follow": lambda *args, **kwargs: cls.robot_follow(*args, **kwargs),
            "robot halt": lambda: cls.robot_stop(),
            "robot perch": lambda *args, **kwargs: cls.robot_perch(*args, **kwargs),
            "robot navigate": lambda *args, **kwargs: cls.robot_navigate(*args, **kwargs),
            "robot gesture": lambda *args, **kwargs: cls.robot_gesture(*args, **kwargs),
            "robot status": lambda: cls.robot_status(),
            "robot calibrate": lambda: cls.robot_calibrate(),
            "robot look": lambda *args, **kwargs: cls.robot_look_at(*args, **kwargs),
            "robot learn location": lambda *args, **kwargs: cls.robot_learn_location(*args, **kwargs),
            "robot go home": lambda: cls.robot_go_home(),
            "robot charge": lambda: cls.robot_charge(),
            "robot express": lambda *args, **kwargs: cls.robot_express(*args, **kwargs),
            "robot personality": lambda *args, **kwargs: cls.robot_set_personality(*args, **kwargs)
        }


def register_robot_scrolls(scroll_engine) -> None:
    """
    Register all robot scrolls with the scroll engine.
    
    Args:
        scroll_engine: ScrollEngine instance
    """
    scrolls = RobotScrolls.get_all_scrolls()
    for name, func in scrolls.items():
        scroll_engine.scrolls[name] = func
    
    print(f"[RobotScrolls] Registered {len(scrolls)} robot scrolls")


# Scroll Actions for use with ScrollAction class
def create_robot_scroll_actions() -> Dict[str, ScrollAction]:
    """
    Create ScrollAction instances for robot control.
    
    Returns:
        Dictionary of scroll name -> ScrollAction
    """
    actions = {}
    for name, func in RobotScrolls.get_all_scrolls().items():
        actions[name] = ScrollAction(func)
    return actions
