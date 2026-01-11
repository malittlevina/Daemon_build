# xr/gesture_interface.py
# Gesture Interface - Hand and body gesture recognition for XR interactions

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum


class GestureType(Enum):
    """Recognized gesture types."""
    # Hand gestures
    PINCH = "pinch"                  # Thumb-index pinch
    GRAB = "grab"                    # Closed fist grab
    POINT = "point"                  # Index finger point
    PALM_UP = "palm_up"              # Open palm facing up
    PALM_DOWN = "palm_down"          # Open palm facing down
    THUMBS_UP = "thumbs_up"          # Thumbs up gesture
    THUMBS_DOWN = "thumbs_down"      # Thumbs down gesture
    PEACE = "peace"                  # Peace/victory sign
    WAVE = "wave"                    # Waving motion
    SWIPE_LEFT = "swipe_left"        # Horizontal swipe left
    SWIPE_RIGHT = "swipe_right"      # Horizontal swipe right
    SWIPE_UP = "swipe_up"            # Vertical swipe up
    SWIPE_DOWN = "swipe_down"        # Vertical swipe down
    TAP = "tap"                      # Air tap gesture
    DOUBLE_TAP = "double_tap"        # Double air tap
    ROTATE = "rotate"                # Rotation gesture
    SCALE = "scale"                  # Two-handed scaling
    
    # Body gestures
    NOD = "nod"                      # Head nod (yes)
    SHAKE = "shake"                  # Head shake (no)
    LEAN_FORWARD = "lean_forward"    # Leaning forward
    STEP_FORWARD = "step_forward"    # Taking a step forward
    STEP_BACK = "step_back"          # Taking a step back


class HandJoint(Enum):
    """Hand skeleton joint names."""
    WRIST = "wrist"
    THUMB_CMC = "thumb_cmc"
    THUMB_MCP = "thumb_mcp"
    THUMB_IP = "thumb_ip"
    THUMB_TIP = "thumb_tip"
    INDEX_MCP = "index_mcp"
    INDEX_PIP = "index_pip"
    INDEX_DIP = "index_dip"
    INDEX_TIP = "index_tip"
    MIDDLE_MCP = "middle_mcp"
    MIDDLE_PIP = "middle_pip"
    MIDDLE_DIP = "middle_dip"
    MIDDLE_TIP = "middle_tip"
    RING_MCP = "ring_mcp"
    RING_PIP = "ring_pip"
    RING_DIP = "ring_dip"
    RING_TIP = "ring_tip"
    PINKY_MCP = "pinky_mcp"
    PINKY_PIP = "pinky_pip"
    PINKY_DIP = "pinky_dip"
    PINKY_TIP = "pinky_tip"


class GestureEvent:
    """Represents a detected gesture event."""
    
    def __init__(
        self,
        gesture_type: GestureType,
        hand: str = "right",
        confidence: float = 1.0,
        position: Optional[Tuple[float, float, float]] = None
    ):
        self.gesture_type = gesture_type
        self.hand = hand  # "left", "right", or "both"
        self.confidence = confidence
        self.position = position
        self.timestamp = datetime.now()
        self.metadata: Dict[str, Any] = {}
        
    def to_dict(self) -> Dict:
        """Serialize gesture event to dictionary."""
        return {
            "gesture": self.gesture_type.value,
            "hand": self.hand,
            "confidence": self.confidence,
            "position": self.position,
            "timestamp": self.timestamp.isoformat()
        }


class GestureBinding:
    """Maps a gesture to an action."""
    
    def __init__(
        self,
        gesture_type: GestureType,
        action: Callable,
        description: str,
        hand: str = "any",
        require_target: bool = False
    ):
        self.gesture_type = gesture_type
        self.action = action
        self.description = description
        self.hand = hand  # "left", "right", "both", "any"
        self.require_target = require_target
        self.enabled = True
        self.invocation_count = 0
        
    def matches(self, event: GestureEvent) -> bool:
        """Check if this binding matches a gesture event."""
        if not self.enabled:
            return False
        if event.gesture_type != self.gesture_type:
            return False
        if self.hand != "any" and event.hand != self.hand:
            return False
        return True


class HandTrackingState:
    """Current state of hand tracking."""
    
    def __init__(self, hand: str):
        self.hand = hand
        self.is_tracked = False
        self.joints: Dict[str, Tuple[float, float, float]] = {}
        self.pinch_strength = 0.0
        self.grab_strength = 0.0
        self.is_pointing = False
        self.palm_position: Optional[Tuple[float, float, float]] = None
        self.palm_normal: Optional[Tuple[float, float, float]] = None
        self.velocity: Tuple[float, float, float] = (0, 0, 0)
        self.last_updated = datetime.now()
        
    def update(self, tracking_data: Dict):
        """Update hand tracking state from sensor data."""
        self.is_tracked = tracking_data.get("is_tracked", False)
        self.joints = tracking_data.get("joints", {})
        self.pinch_strength = tracking_data.get("pinch_strength", 0.0)
        self.grab_strength = tracking_data.get("grab_strength", 0.0)
        self.is_pointing = tracking_data.get("is_pointing", False)
        self.palm_position = tracking_data.get("palm_position")
        self.palm_normal = tracking_data.get("palm_normal")
        self.velocity = tracking_data.get("velocity", (0, 0, 0))
        self.last_updated = datetime.now()


class GestureInterface:
    """
    Gesture recognition and handling for XR interactions.
    
    Provides:
    - Hand gesture detection and classification
    - Gesture-to-action bindings
    - Hand tracking state management
    - Training mode for custom gestures
    - Integration with XR overlay interactions
    """
    
    def __init__(self, xr_engine=None, overlay_manager=None):
        self.xr_engine = xr_engine
        self.overlay_manager = overlay_manager
        self.bindings: List[GestureBinding] = []
        self.gesture_history: List[GestureEvent] = []
        self.left_hand = HandTrackingState("left")
        self.right_hand = HandTrackingState("right")
        self.is_enabled = True
        self.detection_threshold = 0.7
        self.gesture_cooldown = 0.3  # seconds between same gesture
        self.last_gesture_time: Dict[str, float] = {}
        self._setup_default_bindings()
        print("[GestureInterface] Initialized.")
        
    def _setup_default_bindings(self):
        """Set up default gesture-to-action bindings."""
        # Selection and confirmation
        self.bind_gesture(GestureType.PINCH, self._action_select, "Select/Confirm")
        self.bind_gesture(GestureType.TAP, self._action_tap, "Tap to interact")
        self.bind_gesture(GestureType.DOUBLE_TAP, self._action_double_tap, "Quick action")
        
        # Navigation
        self.bind_gesture(GestureType.SWIPE_LEFT, self._action_swipe_left, "Navigate back/previous")
        self.bind_gesture(GestureType.SWIPE_RIGHT, self._action_swipe_right, "Navigate forward/next")
        self.bind_gesture(GestureType.SWIPE_UP, self._action_swipe_up, "Scroll up/expand")
        self.bind_gesture(GestureType.SWIPE_DOWN, self._action_swipe_down, "Scroll down/minimize")
        
        # Object manipulation
        self.bind_gesture(GestureType.GRAB, self._action_grab, "Grab and move")
        self.bind_gesture(GestureType.SCALE, self._action_scale, "Scale object", hand="both")
        self.bind_gesture(GestureType.ROTATE, self._action_rotate, "Rotate object")
        
        # System commands
        self.bind_gesture(GestureType.PALM_UP, self._action_show_menu, "Show menu")
        self.bind_gesture(GestureType.THUMBS_UP, self._action_confirm, "Confirm/Approve")
        self.bind_gesture(GestureType.THUMBS_DOWN, self._action_reject, "Reject/Cancel")
        self.bind_gesture(GestureType.WAVE, self._action_dismiss, "Dismiss/Close")
        
        # Training feedback
        self.bind_gesture(GestureType.NOD, self._action_nod, "Affirmative response")
        self.bind_gesture(GestureType.SHAKE, self._action_shake, "Negative response")
        
    def bind_gesture(
        self,
        gesture_type: GestureType,
        action: Callable,
        description: str,
        hand: str = "any",
        require_target: bool = False
    ) -> GestureBinding:
        """Bind a gesture to an action."""
        binding = GestureBinding(
            gesture_type=gesture_type,
            action=action,
            description=description,
            hand=hand,
            require_target=require_target
        )
        self.bindings.append(binding)
        return binding
    
    def unbind_gesture(self, gesture_type: GestureType, hand: str = "any") -> bool:
        """Remove a gesture binding."""
        original_count = len(self.bindings)
        self.bindings = [
            b for b in self.bindings 
            if not (b.gesture_type == gesture_type and b.hand == hand)
        ]
        return len(self.bindings) < original_count
    
    def process_hand_data(self, hand: str, tracking_data: Dict):
        """
        Process incoming hand tracking data.
        
        Args:
            hand: "left" or "right"
            tracking_data: Raw tracking data from XR system
        """
        if hand == "left":
            self.left_hand.update(tracking_data)
        else:
            self.right_hand.update(tracking_data)
            
    def detect_gesture(self, hand_state: HandTrackingState) -> Optional[GestureEvent]:
        """
        Detect gesture from current hand state.
        
        Args:
            hand_state: Current hand tracking state
            
        Returns:
            Detected gesture event or None
        """
        if not hand_state.is_tracked:
            return None
            
        detected = None
        
        # Pinch detection
        if hand_state.pinch_strength > self.detection_threshold:
            detected = GestureEvent(
                gesture_type=GestureType.PINCH,
                hand=hand_state.hand,
                confidence=hand_state.pinch_strength,
                position=hand_state.palm_position
            )
            
        # Grab detection
        elif hand_state.grab_strength > self.detection_threshold:
            detected = GestureEvent(
                gesture_type=GestureType.GRAB,
                hand=hand_state.hand,
                confidence=hand_state.grab_strength,
                position=hand_state.palm_position
            )
            
        # Point detection
        elif hand_state.is_pointing:
            detected = GestureEvent(
                gesture_type=GestureType.POINT,
                hand=hand_state.hand,
                confidence=0.9,
                position=hand_state.joints.get(HandJoint.INDEX_TIP.value)
            )
            
        # Palm gestures (based on palm normal direction)
        elif hand_state.palm_normal:
            nx, ny, nz = hand_state.palm_normal
            if ny > 0.7:  # Palm facing up
                detected = GestureEvent(
                    gesture_type=GestureType.PALM_UP,
                    hand=hand_state.hand,
                    confidence=ny,
                    position=hand_state.palm_position
                )
            elif ny < -0.7:  # Palm facing down
                detected = GestureEvent(
                    gesture_type=GestureType.PALM_DOWN,
                    hand=hand_state.hand,
                    confidence=abs(ny),
                    position=hand_state.palm_position
                )
                
        # Velocity-based swipe detection
        if hand_state.velocity:
            vx, vy, vz = hand_state.velocity
            swipe_threshold = 1.5  # m/s
            
            if abs(vx) > swipe_threshold:
                gesture = GestureType.SWIPE_RIGHT if vx > 0 else GestureType.SWIPE_LEFT
                detected = GestureEvent(
                    gesture_type=gesture,
                    hand=hand_state.hand,
                    confidence=min(abs(vx) / 2.0, 1.0),
                    position=hand_state.palm_position
                )
            elif abs(vy) > swipe_threshold:
                gesture = GestureType.SWIPE_UP if vy > 0 else GestureType.SWIPE_DOWN
                detected = GestureEvent(
                    gesture_type=gesture,
                    hand=hand_state.hand,
                    confidence=min(abs(vy) / 2.0, 1.0),
                    position=hand_state.palm_position
                )
                
        return detected
    
    def process_gesture(self, event: GestureEvent) -> Optional[Any]:
        """
        Process a detected gesture and invoke matching bindings.
        
        Args:
            event: Detected gesture event
            
        Returns:
            Action result or None
        """
        if not self.is_enabled:
            return None
            
        # Check cooldown
        gesture_key = f"{event.gesture_type.value}_{event.hand}"
        current_time = time.time()
        last_time = self.last_gesture_time.get(gesture_key, 0)
        
        if current_time - last_time < self.gesture_cooldown:
            return None
            
        self.last_gesture_time[gesture_key] = current_time
        
        # Log gesture
        self.gesture_history.append(event)
        if len(self.gesture_history) > 100:
            self.gesture_history = self.gesture_history[-100:]
            
        # Notify XR engine
        if self.xr_engine and self.xr_engine.current_session:
            self.xr_engine.current_session.log_event("gesture_detected", event.to_dict())
            
        # Find and invoke matching bindings
        result = None
        for binding in self.bindings:
            if binding.matches(event):
                try:
                    result = binding.action(event)
                    binding.invocation_count += 1
                    print(f"[GestureInterface] Invoked: {binding.description}")
                except Exception as e:
                    print(f"[GestureInterface] Action error: {e}")
                    
        return result
    
    def update(self) -> List[GestureEvent]:
        """
        Update loop - detect and process gestures from current hand states.
        Call this each frame in the XR loop.
        
        Returns:
            List of detected gesture events
        """
        events = []
        
        # Check left hand
        left_gesture = self.detect_gesture(self.left_hand)
        if left_gesture:
            self.process_gesture(left_gesture)
            events.append(left_gesture)
            
        # Check right hand
        right_gesture = self.detect_gesture(self.right_hand)
        if right_gesture:
            self.process_gesture(right_gesture)
            events.append(right_gesture)
            
        return events
    
    def get_bindings_summary(self) -> List[Dict]:
        """Get summary of all gesture bindings."""
        return [{
            "gesture": b.gesture_type.value,
            "description": b.description,
            "hand": b.hand,
            "enabled": b.enabled,
            "invocations": b.invocation_count
        } for b in self.bindings]
    
    def get_recent_gestures(self, count: int = 10) -> List[Dict]:
        """Get recent gesture history."""
        return [g.to_dict() for g in self.gesture_history[-count:]]
    
    # Default action implementations
    def _action_select(self, event: GestureEvent):
        print(f"[Gesture] Select at {event.position}")
        return {"action": "select", "position": event.position}
    
    def _action_tap(self, event: GestureEvent):
        print(f"[Gesture] Tap at {event.position}")
        return {"action": "tap", "position": event.position}
    
    def _action_double_tap(self, event: GestureEvent):
        print(f"[Gesture] Double tap - quick action")
        return {"action": "double_tap"}
    
    def _action_swipe_left(self, event: GestureEvent):
        print("[Gesture] Swipe left - navigate back")
        return {"action": "navigate", "direction": "back"}
    
    def _action_swipe_right(self, event: GestureEvent):
        print("[Gesture] Swipe right - navigate forward")
        return {"action": "navigate", "direction": "forward"}
    
    def _action_swipe_up(self, event: GestureEvent):
        print("[Gesture] Swipe up - expand")
        return {"action": "scroll", "direction": "up"}
    
    def _action_swipe_down(self, event: GestureEvent):
        print("[Gesture] Swipe down - minimize")
        return {"action": "scroll", "direction": "down"}
    
    def _action_grab(self, event: GestureEvent):
        print(f"[Gesture] Grab at {event.position}")
        return {"action": "grab", "position": event.position}
    
    def _action_scale(self, event: GestureEvent):
        print("[Gesture] Two-handed scale")
        return {"action": "scale"}
    
    def _action_rotate(self, event: GestureEvent):
        print("[Gesture] Rotate")
        return {"action": "rotate"}
    
    def _action_show_menu(self, event: GestureEvent):
        print("[Gesture] Show menu")
        if self.overlay_manager:
            self.overlay_manager.create_info_panel(
                text="XR Menu\n• Settings\n• Training\n• Exit",
                title="Menu",
                position=event.position or (0, 1.5, 1)
            )
        return {"action": "show_menu"}
    
    def _action_confirm(self, event: GestureEvent):
        print("[Gesture] Confirm/Thumbs up")
        return {"action": "confirm", "response": True}
    
    def _action_reject(self, event: GestureEvent):
        print("[Gesture] Reject/Thumbs down")
        return {"action": "reject", "response": False}
    
    def _action_dismiss(self, event: GestureEvent):
        print("[Gesture] Dismiss/Wave")
        if self.overlay_manager:
            self.overlay_manager.clear_group("info_panels")
        return {"action": "dismiss"}
    
    def _action_nod(self, event: GestureEvent):
        print("[Gesture] Nod - affirmative")
        return {"action": "nod", "response": True}
    
    def _action_shake(self, event: GestureEvent):
        print("[Gesture] Head shake - negative")
        return {"action": "shake", "response": False}
