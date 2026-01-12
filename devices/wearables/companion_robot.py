# devices/wearables/companion_robot.py
"""
Companion Robot Interface
=========================
Interface for companion/assistant robots.
Provides physical presence, mobility, and interaction capabilities.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .base_wearable import (
    WearableDevice, WearableType, WearableCapability,
    ConnectionState
)


class RobotMode(Enum):
    """Robot operational modes."""
    IDLE = "idle"
    FOLLOWING = "following"
    PATROLLING = "patrolling"
    GUARDING = "guarding"
    ASSISTING = "assisting"
    CHARGING = "charging"
    AUTONOMOUS = "autonomous"


class EmotionDisplay(Enum):
    """Robot emotional expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    CURIOUS = "curious"
    ALERT = "alert"
    THINKING = "thinking"
    SAD = "sad"
    EXCITED = "excited"
    SLEEPING = "sleeping"


@dataclass
class RobotPosition:
    """Robot position and orientation."""
    x: float = 0.0  # meters from origin
    y: float = 0.0
    z: float = 0.0  # height
    heading: float = 0.0  # degrees, 0 = north
    room: str = "unknown"


@dataclass
class RobotState:
    """Current robot state."""
    mode: RobotMode = RobotMode.IDLE
    position: RobotPosition = field(default_factory=RobotPosition)
    emotion: EmotionDisplay = EmotionDisplay.NEUTRAL
    is_moving: bool = False
    is_speaking: bool = False
    obstacle_detected: bool = False
    person_nearby: bool = False
    battery_level: float = 100.0


class CompanionRobot(WearableDevice):
    """
    Companion Robot - physical AI assistant.
    
    Capabilities:
    - Mobility: Navigate home/office environment
    - Camera/Vision: See and recognize people/objects
    - Speaker/Microphone: Voice interaction
    - Display: Show emotions/information
    - Manipulation: Carry small items (optional)
    - Sensors: Detect obstacles, people, environment
    """
    
    DEFAULT_CAPABILITIES = [
        WearableCapability.CAMERA,
        WearableCapability.DEPTH_CAMERA,
        WearableCapability.MICROPHONE,
        WearableCapability.SPEAKER,
        WearableCapability.DISPLAY,
        WearableCapability.MOBILITY,
        WearableCapability.GPS,
        WearableCapability.LIDAR,
        WearableCapability.BLUETOOTH,
        WearableCapability.WIFI,
    ]
    
    def __init__(self, device_id: str, name: str = "Companion Robot"):
        super().__init__(
            device_id=device_id,
            name=name,
            wearable_type=WearableType.ROBOT,
            capabilities=self.DEFAULT_CAPABILITIES
        )
        
        self.state = RobotState()
        self.home_position = RobotPosition(x=0, y=0, room="charging_station")
        
        # Navigation
        self.known_locations: Dict[str, RobotPosition] = {}
        self.current_path: List[RobotPosition] = []
        
        # People
        self.known_people: Dict[str, Dict] = {}
        self.following_target: Optional[str] = None
        
        print(f"[Robot] Initialized: {name}")
    
    def connect(self) -> bool:
        """Connect to the robot."""
        self.status.connection_state = ConnectionState.CONNECTING
        print(f"[Robot] Connecting to {self.name}...")
        
        time.sleep(0.5)
        
        self.status.connection_state = ConnectionState.CONNECTED
        self.status.last_sync = time.time()
        self.set_emotion(EmotionDisplay.HAPPY)
        
        print(f"[Robot] Connected to {self.name}")
        self.emit('connected', self.to_dict())
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from the robot."""
        self.stop()
        self.set_emotion(EmotionDisplay.SLEEPING)
        self.status.connection_state = ConnectionState.DISCONNECTED
        print(f"[Robot] Disconnected from {self.name}")
        self.emit('disconnected', self.to_dict())
        return True
    
    def sync(self) -> Dict[str, Any]:
        """Sync state from robot."""
        self._sensor_data = {
            'mode': self.state.mode.value,
            'position': {
                'x': self.state.position.x,
                'y': self.state.position.y,
                'room': self.state.position.room,
                'heading': self.state.position.heading
            },
            'emotion': self.state.emotion.value,
            'is_moving': self.state.is_moving,
            'battery': self.state.battery_level,
            'obstacle': self.state.obstacle_detected,
            'person_nearby': self.state.person_nearby
        }
        
        self.status.last_sync = time.time()
        self.status.battery_level = self.state.battery_level
        return self._sensor_data
    
    # ==================
    # Movement
    # ==================
    
    def move_to(self, destination: str) -> bool:
        """Move to a named location."""
        if destination in self.known_locations:
            target = self.known_locations[destination]
            return self._navigate_to(target)
        
        # Try to find room
        print(f"[Robot] Searching for: {destination}")
        self.set_emotion(EmotionDisplay.THINKING)
        
        # In production, would use SLAM/mapping
        return False
    
    def _navigate_to(self, target: RobotPosition) -> bool:
        """Navigate to a position."""
        self.state.is_moving = True
        self.state.mode = RobotMode.AUTONOMOUS
        self.set_emotion(EmotionDisplay.CURIOUS)
        
        print(f"[Robot] Navigating to {target.room}...")
        self.emit('navigation_started', {'target': target.room})
        
        # Simulate movement
        def move():
            time.sleep(2)  # Would actually navigate
            self.state.position = target
            self.state.is_moving = False
            self.state.mode = RobotMode.IDLE
            self.set_emotion(EmotionDisplay.HAPPY)
            print(f"[Robot] Arrived at {target.room}")
            self.emit('navigation_complete', {'location': target.room})
        
        threading.Thread(target=move, daemon=True).start()
        return True
    
    def follow(self, person_id: str = "user") -> bool:
        """Follow a person."""
        self.state.mode = RobotMode.FOLLOWING
        self.following_target = person_id
        self.set_emotion(EmotionDisplay.CURIOUS)
        
        print(f"[Robot] Following {person_id}")
        self.emit('following_started', {'target': person_id})
        return True
    
    def stop_following(self):
        """Stop following."""
        if self.state.mode == RobotMode.FOLLOWING:
            self.state.mode = RobotMode.IDLE
            self.following_target = None
            print("[Robot] Stopped following")
    
    def patrol(self, locations: List[str] = None):
        """Patrol between locations."""
        self.state.mode = RobotMode.PATROLLING
        self.set_emotion(EmotionDisplay.ALERT)
        
        patrol_points = locations or list(self.known_locations.keys())
        print(f"[Robot] Patrolling: {patrol_points}")
        self.emit('patrol_started', {'locations': patrol_points})
    
    def go_home(self) -> bool:
        """Return to charging station."""
        return self._navigate_to(self.home_position)
    
    def stop(self):
        """Stop all movement."""
        self.state.is_moving = False
        self.state.mode = RobotMode.IDLE
        self.following_target = None
        print("[Robot] Stopped")
    
    # ==================
    # Perception
    # ==================
    
    def look_around(self) -> Dict[str, Any]:
        """Scan surroundings."""
        self.set_emotion(EmotionDisplay.CURIOUS)
        
        # In production, use camera/lidar
        scan_result = {
            'objects': ['couch', 'table', 'lamp'],
            'people': [],
            'obstacles': [],
            'open_paths': ['north', 'east'],
            'current_room': self.state.position.room
        }
        
        self.emit('scan_complete', scan_result)
        return scan_result
    
    def find_person(self, person_id: str = None) -> Optional[Dict]:
        """Look for a person."""
        self.set_emotion(EmotionDisplay.CURIOUS)
        print(f"[Robot] Looking for {person_id or 'anyone'}...")
        
        # In production, use face recognition
        return None
    
    def recognize_person(self) -> Optional[str]:
        """Recognize person in view."""
        # Would use face recognition
        return None
    
    # ==================
    # Interaction
    # ==================
    
    def speak(self, text: str) -> bool:
        """Speak through robot."""
        self.state.is_speaking = True
        self.set_emotion(EmotionDisplay.HAPPY)
        
        print(f"[Robot] Speaking: {text}")
        self.emit('speaking', {'text': text})
        
        # Simulate speaking duration
        def finish_speaking():
            time.sleep(len(text) * 0.05)
            self.state.is_speaking = False
        
        threading.Thread(target=finish_speaking, daemon=True).start()
        return True
    
    def set_emotion(self, emotion: EmotionDisplay):
        """Set robot's displayed emotion."""
        self.state.emotion = emotion
        self.emit('emotion_changed', {'emotion': emotion.value})
    
    def play_animation(self, animation: str) -> bool:
        """Play an animation."""
        animations = ['wave', 'nod', 'shake_head', 'dance', 'bow', 'celebrate']
        
        if animation in animations:
            print(f"[Robot] Playing animation: {animation}")
            self.emit('animation', {'name': animation})
            return True
        return False
    
    def show_display(self, content: str, display_type: str = "text"):
        """Show content on robot's display."""
        print(f"[Robot] Display: {content}")
        self.emit('display', {'content': content, 'type': display_type})
    
    # ==================
    # Assistance
    # ==================
    
    def carry_item(self, item: str, destination: str) -> bool:
        """Carry an item to a destination."""
        if not self.has_capability(WearableCapability.MANIPULATION):
            self.speak(f"I can lead you to {destination}, but I cannot carry items.")
            return False
        
        print(f"[Robot] Carrying {item} to {destination}")
        self.speak(f"I'll bring the {item} to {destination}")
        return self.move_to(destination)
    
    def alert(self, message: str, urgent: bool = False):
        """Alert/notify user."""
        if urgent:
            self.set_emotion(EmotionDisplay.ALERT)
            self.speak(f"Urgent: {message}")
        else:
            self.speak(message)
        
        self.emit('alert', {'message': message, 'urgent': urgent})
    
    def remind(self, reminder: str, in_minutes: float = 0):
        """Set a reminder."""
        if in_minutes > 0:
            def do_remind():
                time.sleep(in_minutes * 60)
                self.alert(reminder)
            threading.Thread(target=do_remind, daemon=True).start()
            self.speak(f"I'll remind you in {in_minutes} minutes")
        else:
            self.alert(reminder)
    
    # ==================
    # Learning
    # ==================
    
    def learn_location(self, name: str):
        """Learn current location with a name."""
        self.known_locations[name] = RobotPosition(
            x=self.state.position.x,
            y=self.state.position.y,
            z=self.state.position.z,
            heading=self.state.position.heading,
            room=name
        )
        print(f"[Robot] Learned location: {name}")
        self.speak(f"I've memorized this location as {name}")
    
    def learn_person(self, person_id: str, name: str = None):
        """Learn to recognize a person."""
        self.known_people[person_id] = {
            'name': name or person_id,
            'learned_at': time.time()
        }
        print(f"[Robot] Learned person: {name or person_id}")
        self.speak(f"Nice to meet you, {name or person_id}")
    
    # ==================
    # Commands
    # ==================
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send command to robot."""
        params = params or {}
        
        if command == 'move_to':
            return self.move_to(params.get('destination', 'home'))
        elif command == 'follow':
            return self.follow(params.get('target', 'user'))
        elif command == 'stop':
            self.stop()
            return True
        elif command == 'speak':
            return self.speak(params.get('text', ''))
        elif command == 'emotion':
            try:
                emotion = EmotionDisplay(params.get('emotion', 'neutral'))
                self.set_emotion(emotion)
                return True
            except ValueError:
                return False
        elif command == 'patrol':
            self.patrol(params.get('locations'))
            return True
        elif command == 'go_home':
            return self.go_home()
        elif command == 'look':
            self.look_around()
            return True
        elif command == 'animate':
            return self.play_animation(params.get('animation', 'wave'))
        
        return False
