# robotics/companion.py
"""
Companion Behaviors for the Miniature Robot.

Provides high-level behavior patterns for a companion robot that:
- Can hang on the user (perched mode)
- Can follow the user around
- Expresses personality through gestures
- Responds to touch and proximity
"""

import time
import random
import math
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass


class CompanionMood(Enum):
    """Mood states that influence behavior."""
    HAPPY = "happy"
    CURIOUS = "curious"
    ALERT = "alert"
    SLEEPY = "sleepy"
    PLAYFUL = "playful"
    CALM = "calm"


class AttentionFocus(Enum):
    """What the companion is focused on."""
    USER = "user"
    ENVIRONMENT = "environment"
    TASK = "task"
    REST = "rest"
    NONE = "none"


@dataclass
class PerchConfig:
    """Configuration for perching on user."""
    location: str = "shoulder"  # shoulder, arm, pocket
    grip_strength: float = 0.7  # 0-1
    balance_sensitivity: float = 0.8
    dismount_on_request: bool = True


@dataclass
class FollowConfig:
    """Configuration for following behavior."""
    distance: float = 1.0  # meters
    speed_factor: float = 0.8  # fraction of max speed
    path_smoothing: float = 0.5
    obstacle_caution: float = 0.7


class CompanionBehaviors:
    """
    High-level behavior controller for the companion robot.
    
    Manages:
    - Perching on user
    - Following user
    - Idle behaviors
    - Gestural expression
    - Mood-based behavior modulation
    """
    
    # Idle behavior timing
    IDLE_LOOK_INTERVAL = (3.0, 8.0)  # seconds
    IDLE_GESTURE_INTERVAL = (10.0, 30.0)
    IDLE_MICRO_MOVEMENT_INTERVAL = (0.5, 2.0)
    
    # Following behavior timing  
    FOLLOW_USER_CHECK_INTERVAL = 0.1  # seconds
    FOLLOW_GESTURE_INTERVAL = (15.0, 45.0)
    
    def __init__(self, robot_core):
        """
        Initialize companion behaviors.
        
        Args:
            robot_core: RobotCore instance for accessing subsystems
        """
        self.core = robot_core
        
        # Current state
        self.mood = CompanionMood.CALM
        self.attention = AttentionFocus.NONE
        self.is_active = False
        
        # Configuration
        self.perch_config = PerchConfig()
        self.follow_config = FollowConfig()
        
        # Timing
        self._last_idle_look = 0.0
        self._last_idle_gesture = 0.0
        self._last_micro_movement = 0.0
        self._last_follow_gesture = 0.0
        self._next_idle_look_time = 0.0
        self._next_idle_gesture_time = 0.0
        
        # Personality traits (influence behavior)
        self.personality = {
            "curiosity": 0.7,      # How often it looks around
            "playfulness": 0.5,   # How often it does gestures
            "calmness": 0.6,      # How smooth/slow movements are
            "affection": 0.8,     # How focused on user
            "energy": 0.5         # Activity level
        }
        
        # Touch response callbacks
        self._touch_callbacks: List[Callable] = []
        
        print("[CompanionBehaviors] Initialized")
    
    def set_follow_distance(self, distance: float) -> None:
        """Set the target following distance."""
        self.follow_config.distance = max(0.5, min(3.0, distance))
        print(f"[CompanionBehaviors] Follow distance: {self.follow_config.distance}m")
    
    def set_perch_location(self, location: str) -> None:
        """Set the perching location."""
        valid_locations = ["shoulder", "arm", "pocket", "backpack", "desk"]
        if location.lower() in valid_locations:
            self.perch_config.location = location.lower()
            print(f"[CompanionBehaviors] Perch location: {self.perch_config.location}")
        else:
            print(f"[CompanionBehaviors] Unknown perch location: {location}")
    
    def follow_behavior(self) -> None:
        """
        Execute following behavior.
        Called from control loop when in following mode.
        """
        self.attention = AttentionFocus.USER
        current_time = time.time()
        
        # Update navigation following
        self.core.navigation.start_following(self.follow_config.distance)
        
        # Occasional gesture to show engagement
        if current_time - self._last_follow_gesture > self._get_random_interval(self.FOLLOW_GESTURE_INTERVAL):
            self._do_following_gesture()
            self._last_follow_gesture = current_time
        
        # Adjust mood based on proximity
        proximity = self.core.state.environmental.user_proximity
        if proximity == "near":
            self.mood = CompanionMood.HAPPY
        elif proximity == "far":
            self.mood = CompanionMood.ALERT
    
    def _do_following_gesture(self) -> None:
        """Perform a gesture while following."""
        gestures = ["attention", "happy", "curious"]
        weights = [0.4, 0.4, 0.2]
        
        if self.mood == CompanionMood.HAPPY:
            weights = [0.2, 0.6, 0.2]
        elif self.mood == CompanionMood.ALERT:
            weights = [0.6, 0.2, 0.2]
        
        gesture = random.choices(gestures, weights=weights)[0]
        self.core.motion.start_gesture(gesture)
    
    def perched_behavior(self) -> None:
        """
        Execute perched behavior.
        Called from control loop when in perched mode.
        """
        self.attention = AttentionFocus.USER
        
        # Maintain grip
        self._maintain_grip()
        
        # Subtle movements to show awareness
        self._do_perched_movements()
        
        # Check for touch
        self._check_touch_response()
    
    def _maintain_grip(self) -> None:
        """Maintain appropriate grip while perched."""
        # Read grip force sensors
        left_force = self.core.state.physical.grip_force
        target_force = self.perch_config.grip_strength
        
        # Adjust grip if needed
        current_grip = self.core.hal.get_motor_position("grip_left")
        if current_grip is not None:
            # Increase grip if slipping, decrease if too tight
            adjustment = 0.0
            if left_force < target_force * 0.8:
                adjustment = 2.0  # degrees
            elif left_force > target_force * 1.2:
                adjustment = -2.0
            
            if abs(adjustment) > 0:
                new_grip = current_grip + adjustment
                self.core.motion.set_grip(new_grip / 90.0)  # Normalize to 0-1
    
    def _do_perched_movements(self) -> None:
        """Subtle movements while perched."""
        current_time = time.time()
        
        # Micro-movements (breathing effect)
        if current_time - self._last_micro_movement > self._get_random_interval(self.IDLE_MICRO_MOVEMENT_INTERVAL):
            # Tiny head movements
            pan_offset = random.gauss(0, 2)  # Small random pan
            tilt_offset = random.gauss(0, 1)  # Small random tilt
            
            current_pan = self.core.hal.get_motor_position("neck_pan") or 0
            current_tilt = self.core.hal.get_motor_position("neck_tilt") or 0
            
            self.core.motion.look_at(
                current_pan + pan_offset,
                current_tilt + tilt_offset
            )
            self._last_micro_movement = current_time
    
    def _check_touch_response(self) -> None:
        """Check and respond to touch input."""
        touch = self.core.hal.sensor_readings.get("touch_head")
        if touch and touch.value:
            # Respond to head touch
            self.mood = CompanionMood.HAPPY
            self.core.motion.start_gesture("nod")
            
            for callback in self._touch_callbacks:
                try:
                    callback("head", touch.value)
                except Exception as e:
                    print(f"[CompanionBehaviors] Touch callback error: {e}")
    
    def idle_behavior(self) -> None:
        """
        Execute idle behavior.
        Called from control loop when in idle mode.
        """
        self.attention = AttentionFocus.ENVIRONMENT
        current_time = time.time()
        
        # Look around occasionally
        if current_time - self._last_idle_look > self._next_idle_look_time:
            self._do_idle_look()
            self._last_idle_look = current_time
            self._next_idle_look_time = self._get_random_interval(self.IDLE_LOOK_INTERVAL)
        
        # Occasional gesture
        if current_time - self._last_idle_gesture > self._next_idle_gesture_time:
            self._do_idle_gesture()
            self._last_idle_gesture = current_time
            self._next_idle_gesture_time = self._get_random_interval(self.IDLE_GESTURE_INTERVAL)
        
        # Transition to sleepy if idle for too long
        time_idle = current_time - self.core.state.context.get("last_interaction", current_time)
        if time_idle > 300:  # 5 minutes
            self.mood = CompanionMood.SLEEPY
    
    def _do_idle_look(self) -> None:
        """Look around while idle."""
        # Personality affects how much we look around
        curiosity = self.personality["curiosity"]
        
        # Random look direction
        pan = random.uniform(-45, 45) * curiosity
        tilt = random.uniform(-10, 30) * curiosity
        
        self.core.motion.look_at(pan, tilt)
    
    def _do_idle_gesture(self) -> None:
        """Perform an idle gesture."""
        playfulness = self.personality["playfulness"]
        
        # Gesture selection based on mood and personality
        if self.mood == CompanionMood.SLEEPY:
            if random.random() < 0.7:
                self.core.motion.start_gesture("sleep")
            return
        
        if random.random() < playfulness:
            gestures = ["look_around", "curious", "nod"]
            self.core.motion.start_gesture(random.choice(gestures))
    
    def perform_gesture(self, gesture_name: str) -> bool:
        """
        Perform a named gesture.
        
        Args:
            gesture_name: Name of gesture
            
        Returns:
            True if gesture started
        """
        # Update mood based on gesture
        mood_gestures = {
            "happy": CompanionMood.HAPPY,
            "sad": CompanionMood.CALM,
            "curious": CompanionMood.CURIOUS,
            "wave": CompanionMood.PLAYFUL,
            "attention": CompanionMood.ALERT
        }
        
        if gesture_name in mood_gestures:
            self.mood = mood_gestures[gesture_name]
        
        return self.core.motion.start_gesture(gesture_name)
    
    def react_to_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        React to an external event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        reactions = {
            "user_greeting": lambda: self._react_greeting(),
            "user_leaving": lambda: self._react_leaving(),
            "loud_sound": lambda: self._react_sound(),
            "obstacle_detected": lambda: self._react_obstacle(),
            "low_battery": lambda: self._react_low_battery(),
            "task_complete": lambda: self._react_task_complete()
        }
        
        handler = reactions.get(event_type)
        if handler:
            handler()
    
    def _react_greeting(self) -> None:
        """React to user greeting."""
        self.mood = CompanionMood.HAPPY
        self.attention = AttentionFocus.USER
        self.core.motion.start_gesture("happy")
    
    def _react_leaving(self) -> None:
        """React to user leaving."""
        self.core.motion.start_gesture("sad")
        self.mood = CompanionMood.CALM
    
    def _react_sound(self) -> None:
        """React to loud sound."""
        self.mood = CompanionMood.ALERT
        self.core.motion.start_gesture("attention")
    
    def _react_obstacle(self) -> None:
        """React to obstacle detection."""
        self.core.motion.look_at(0, 30)  # Look at obstacle
        self.core.motion.start_gesture("curious")
    
    def _react_low_battery(self) -> None:
        """React to low battery."""
        self.mood = CompanionMood.SLEEPY
        self.core.motion.start_gesture("sleep")
    
    def _react_task_complete(self) -> None:
        """React to completing a task."""
        self.mood = CompanionMood.HAPPY
        self.core.motion.start_gesture("happy")
    
    def _get_random_interval(self, interval_range: tuple) -> float:
        """Get a random time interval within range."""
        return random.uniform(interval_range[0], interval_range[1])
    
    def set_personality_trait(self, trait: str, value: float) -> None:
        """
        Set a personality trait value.
        
        Args:
            trait: Trait name
            value: Value 0-1
        """
        if trait in self.personality:
            self.personality[trait] = max(0.0, min(1.0, value))
            print(f"[CompanionBehaviors] Set {trait} = {self.personality[trait]}")
    
    def register_touch_callback(self, callback: Callable) -> None:
        """Register a callback for touch events."""
        self._touch_callbacks.append(callback)
    
    def attach_to_user(self) -> bool:
        """
        Initiate attachment/perching sequence.
        
        Returns:
            True if attachment started
        """
        from robotics.robot_core import RobotMode
        
        print(f"[CompanionBehaviors] Initiating perch at {self.perch_config.location}")
        
        # Close grip gradually
        for grip_level in [0.2, 0.4, 0.6, 0.8]:
            self.core.motion.set_grip(grip_level)
            time.sleep(0.3)
        
        # Set final grip based on config
        self.core.motion.set_grip(self.perch_config.grip_strength)
        
        # Update state
        self.core.set_mode(RobotMode.PERCHED)
        self.core.state.set("flags.is_perched", True)
        
        # Happy gesture
        self.core.motion.start_gesture("happy")
        
        return True
    
    def detach_from_user(self) -> bool:
        """
        Initiate detachment sequence.
        
        Returns:
            True if detachment successful
        """
        from robotics.robot_core import RobotMode
        
        print("[CompanionBehaviors] Detaching from user")
        
        # Release grip gradually
        for grip_level in [0.6, 0.4, 0.2, 0.0]:
            self.core.motion.set_grip(grip_level)
            time.sleep(0.2)
        
        # Update state
        self.core.set_mode(RobotMode.IDLE)
        self.core.state.set("flags.is_perched", False)
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get companion behavior status."""
        return {
            "mood": self.mood.value,
            "attention": self.attention.value,
            "personality": self.personality.copy(),
            "perch_config": {
                "location": self.perch_config.location,
                "grip_strength": self.perch_config.grip_strength
            },
            "follow_config": {
                "distance": self.follow_config.distance,
                "speed_factor": self.follow_config.speed_factor
            }
        }
    
    def sync_with_emotion_engine(self) -> None:
        """
        Sync mood with daemon's emotion engine.
        
        Integrates with emotion/emotion_engine.py
        """
        try:
            from emotion.emotion_engine import EmotionEngine
            
            # Map companion mood to emotion state
            mood_to_emotion = {
                CompanionMood.HAPPY: "joy",
                CompanionMood.CURIOUS: "curiosity",
                CompanionMood.ALERT: "attention",
                CompanionMood.SLEEPY: "calm",
                CompanionMood.PLAYFUL: "excitement",
                CompanionMood.CALM: "neutral"
            }
            
            emotion = mood_to_emotion.get(self.mood, "neutral")
            self.core.state.behavioral.emotional_state = emotion
            
        except ImportError:
            pass  # Emotion engine not available
