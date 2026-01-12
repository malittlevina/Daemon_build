# devices/wearables/smart_glasses.py
"""
Smart Glasses Interface
=======================
Interface for smart glasses/AR headsets (like Ray-Ban Meta, Xreal, etc.)
Provides visual input, audio, and AR overlay capabilities.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .base_wearable import (
    WearableDevice, WearableType, WearableCapability,
    ConnectionState
)


class ARLayerType(Enum):
    """Types of AR overlay content."""
    TEXT = "text"
    NOTIFICATION = "notification"
    NAVIGATION = "navigation"
    OBJECT_LABEL = "object_label"
    TRANSLATION = "translation"
    REMINDER = "reminder"
    ASSISTANT = "assistant"
    DEBUG = "debug"


@dataclass
class ARElement:
    """An AR element to display."""
    layer_type: ARLayerType
    content: str
    position: str = "center"  # center, top, bottom, left, right
    duration_seconds: float = 5.0
    color: str = "white"
    size: str = "medium"
    icon: Optional[str] = None


@dataclass
class VisualContext:
    """What the glasses see."""
    scene_description: str = ""
    detected_objects: List[str] = field(default_factory=list)
    detected_text: List[str] = field(default_factory=list)
    detected_faces: int = 0
    lighting: str = "normal"
    is_outdoor: bool = False
    timestamp: float = 0.0


class SmartGlasses(WearableDevice):
    """
    Smart Glasses - provides visual observation and AR overlay.
    
    Capabilities:
    - Camera for visual input
    - Microphone for voice input
    - Speaker for audio output
    - AR display for overlays
    - GPS for location
    - Motion tracking for head gestures
    """
    
    DEFAULT_CAPABILITIES = [
        WearableCapability.CAMERA,
        WearableCapability.MICROPHONE,
        WearableCapability.SPEAKER,
        WearableCapability.AR_OVERLAY,
        WearableCapability.DISPLAY,
        WearableCapability.GPS,
        WearableCapability.MOTION,
        WearableCapability.BLUETOOTH,
        WearableCapability.WIFI,
    ]
    
    # Voice commands
    VOICE_COMMANDS = [
        "hey prometheus",
        "take photo",
        "record video",
        "translate",
        "navigate to",
        "remind me",
        "what am i looking at",
        "who is this",
        "read this",
    ]
    
    def __init__(self, device_id: str, name: str = "Smart Glasses"):
        super().__init__(
            device_id=device_id,
            name=name,
            wearable_type=WearableType.GLASSES,
            capabilities=self.DEFAULT_CAPABILITIES
        )
        
        # Visual context
        self.current_view = VisualContext()
        self.view_history: List[VisualContext] = []
        
        # AR state
        self.ar_elements: List[ARElement] = []
        self._ar_enabled = False
        
        # Audio state
        self._is_listening = False
        self._is_recording = False
        
        print(f"[SmartGlasses] Initialized: {name}")
    
    def connect(self) -> bool:
        """Connect to the glasses."""
        self.status.connection_state = ConnectionState.CONNECTING
        print(f"[SmartGlasses] Connecting to {self.name}...")
        
        time.sleep(0.5)
        
        self.status.connection_state = ConnectionState.CONNECTED
        self.status.is_worn = True
        self.status.last_sync = time.time()
        
        print(f"[SmartGlasses] Connected to {self.name}")
        self.emit('connected', self.to_dict())
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from the glasses."""
        self.stop_listening()
        self.clear_ar()
        self.status.connection_state = ConnectionState.DISCONNECTED
        self.status.is_worn = False
        print(f"[SmartGlasses] Disconnected from {self.name}")
        self.emit('disconnected', self.to_dict())
        return True
    
    def sync(self) -> Dict[str, Any]:
        """Sync data from glasses."""
        if self.status.connection_state != ConnectionState.CONNECTED:
            return {'error': 'Not connected'}
        
        self._sensor_data = {
            'is_worn': self.status.is_worn,
            'ar_enabled': self._ar_enabled,
            'ar_elements': len(self.ar_elements),
            'is_listening': self._is_listening,
            'battery': self.status.battery_level,
        }
        
        self.status.last_sync = time.time()
        return self._sensor_data
    
    # ==================
    # Camera/Vision
    # ==================
    
    def capture_view(self) -> VisualContext:
        """Capture and analyze current view."""
        # In production, this would:
        # 1. Capture image from glasses camera
        # 2. Run through vision model for scene understanding
        # 3. Detect objects, text, faces
        
        self.current_view = VisualContext(
            scene_description="Indoor office environment",
            detected_objects=["desk", "computer", "chair", "window"],
            detected_text=[],
            detected_faces=0,
            lighting="normal",
            is_outdoor=False,
            timestamp=time.time()
        )
        
        self.view_history.append(self.current_view)
        if len(self.view_history) > 100:
            self.view_history = self.view_history[-50:]
        
        self.emit('view_captured', {
            'scene': self.current_view.scene_description,
            'objects': self.current_view.detected_objects
        })
        
        return self.current_view
    
    def take_photo(self) -> Dict[str, Any]:
        """Take a photo."""
        timestamp = time.time()
        photo_id = f"photo_{int(timestamp)}"
        
        print(f"[SmartGlasses] Photo captured: {photo_id}")
        self.emit('photo_taken', {'photo_id': photo_id, 'timestamp': timestamp})
        
        return {'photo_id': photo_id, 'timestamp': timestamp}
    
    def start_recording(self, duration_seconds: float = None) -> bool:
        """Start video recording."""
        if self._is_recording:
            return False
        
        self._is_recording = True
        print(f"[SmartGlasses] Recording started")
        self.emit('recording_started', {'duration': duration_seconds})
        
        if duration_seconds:
            def stop_after():
                time.sleep(duration_seconds)
                self.stop_recording()
            threading.Thread(target=stop_after, daemon=True).start()
        
        return True
    
    def stop_recording(self) -> Dict[str, Any]:
        """Stop video recording."""
        if not self._is_recording:
            return {'error': 'Not recording'}
        
        self._is_recording = False
        print("[SmartGlasses] Recording stopped")
        self.emit('recording_stopped', {})
        
        return {'status': 'stopped'}
    
    def analyze_scene(self) -> Dict[str, Any]:
        """Get AI analysis of current scene."""
        view = self.capture_view()
        
        # In production, send to vision model
        analysis = {
            'scene': view.scene_description,
            'objects': view.detected_objects,
            'people': view.detected_faces,
            'text': view.detected_text,
            'environment': 'outdoor' if view.is_outdoor else 'indoor',
            'lighting': view.lighting,
            'suggestions': []
        }
        
        return analysis
    
    # ==================
    # AR Overlay
    # ==================
    
    def enable_ar(self):
        """Enable AR overlay."""
        self._ar_enabled = True
        print("[SmartGlasses] AR enabled")
        self.emit('ar_enabled', {})
    
    def disable_ar(self):
        """Disable AR overlay."""
        self._ar_enabled = False
        self.clear_ar()
        print("[SmartGlasses] AR disabled")
        self.emit('ar_disabled', {})
    
    def show_ar(
        self,
        content: str,
        layer_type: ARLayerType = ARLayerType.TEXT,
        position: str = "center",
        duration: float = 5.0,
        icon: str = None
    ) -> ARElement:
        """Display AR content."""
        if not self._ar_enabled:
            self.enable_ar()
        
        element = ARElement(
            layer_type=layer_type,
            content=content,
            position=position,
            duration_seconds=duration,
            icon=icon
        )
        
        self.ar_elements.append(element)
        print(f"[SmartGlasses] AR: {content}")
        self.emit('ar_displayed', {'content': content, 'type': layer_type.value})
        
        # Auto-remove after duration
        def remove_after():
            time.sleep(duration)
            if element in self.ar_elements:
                self.ar_elements.remove(element)
        
        threading.Thread(target=remove_after, daemon=True).start()
        
        return element
    
    def show_notification(self, title: str, message: str, icon: str = "🔔"):
        """Show AR notification."""
        content = f"{icon} {title}: {message}"
        return self.show_ar(content, ARLayerType.NOTIFICATION, "top", 5.0)
    
    def show_navigation(self, direction: str, distance: str):
        """Show navigation overlay."""
        content = f"➡️ {direction} in {distance}"
        return self.show_ar(content, ARLayerType.NAVIGATION, "bottom", 10.0)
    
    def show_translation(self, original: str, translated: str):
        """Show translation overlay."""
        content = f"🌐 {original} → {translated}"
        return self.show_ar(content, ARLayerType.TRANSLATION, "center", 8.0)
    
    def show_object_label(self, label: str, confidence: float = 1.0):
        """Label an object in view."""
        content = f"📦 {label} ({int(confidence * 100)}%)"
        return self.show_ar(content, ARLayerType.OBJECT_LABEL, "center", 3.0)
    
    def clear_ar(self):
        """Clear all AR elements."""
        self.ar_elements.clear()
        print("[SmartGlasses] AR cleared")
    
    # ==================
    # Audio
    # ==================
    
    def start_listening(self):
        """Start listening for voice commands."""
        if self._is_listening:
            return
        
        self._is_listening = True
        print("[SmartGlasses] Listening for voice commands...")
        self.emit('listening_started', {})
    
    def stop_listening(self):
        """Stop listening for voice commands."""
        self._is_listening = False
        print("[SmartGlasses] Stopped listening")
        self.emit('listening_stopped', {})
    
    def speak(self, text: str, voice: str = "default") -> bool:
        """Speak through the glasses speakers."""
        if not self.has_capability(WearableCapability.SPEAKER):
            return False
        
        print(f"[SmartGlasses] Speaking: {text}")
        self.emit('speaking', {'text': text})
        return True
    
    def play_audio(self, audio_id: str) -> bool:
        """Play audio through speakers."""
        print(f"[SmartGlasses] Playing audio: {audio_id}")
        return True
    
    # ==================
    # Commands
    # ==================
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send command to glasses."""
        params = params or {}
        
        if command == 'photo':
            self.take_photo()
            return True
        elif command == 'record':
            return self.start_recording(params.get('duration'))
        elif command == 'stop_record':
            self.stop_recording()
            return True
        elif command == 'notify':
            self.show_notification(
                params.get('title', 'Notification'),
                params.get('message', '')
            )
            return True
        elif command == 'speak':
            return self.speak(params.get('text', ''))
        elif command == 'analyze':
            self.analyze_scene()
            return True
        elif command == 'ar_show':
            self.show_ar(params.get('content', ''))
            return True
        elif command == 'ar_clear':
            self.clear_ar()
            return True
        
        return False
