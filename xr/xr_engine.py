# xr/xr_engine.py
# Core XR Engine for ThothOS Daemon - Manages AR/VR/MR sessions and device interfaces

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class XRMode(Enum):
    """Extended Reality operation modes."""
    INACTIVE = "inactive"
    AR = "augmented_reality"       # Augmented Reality - overlays on real world
    VR = "virtual_reality"         # Virtual Reality - fully immersive
    MR = "mixed_reality"           # Mixed Reality - blended environments
    PASSTHROUGH = "passthrough"    # Passthrough with minimal augmentation


class XRDeviceType(Enum):
    """Supported XR device types."""
    HEADSET = "headset"            # HMD devices (Quest, Vision Pro, etc.)
    GLASSES = "glasses"            # AR glasses (smart glasses)
    PHONE_AR = "phone_ar"          # Phone-based AR (ARKit/ARCore)
    PROJECTION = "projection"      # Projection-based AR
    HOLOGRAPHIC = "holographic"    # Holographic displays
    SIMULATED = "simulated"        # Software simulation for testing


class XRSession:
    """Represents an active XR session with state tracking."""
    
    def __init__(self, session_id: str, mode: XRMode, device_type: XRDeviceType):
        self.session_id = session_id
        self.mode = mode
        self.device_type = device_type
        self.started_at = datetime.now()
        self.is_active = True
        self.spatial_anchors = []
        self.overlays = []
        self.training_context = None
        self.event_log = []
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event that occurred during this session."""
        self.event_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        })
        
    def to_dict(self) -> Dict:
        """Serialize session to dictionary."""
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "device_type": self.device_type.value,
            "started_at": self.started_at.isoformat(),
            "is_active": self.is_active,
            "anchors_count": len(self.spatial_anchors),
            "overlays_count": len(self.overlays),
            "event_count": len(self.event_log)
        }


class XREngine:
    """
    Core XR Engine - Manages AR/VR/MR sessions and coordinates with daemon subsystems.
    
    Integrates with:
    - VisionSensor for camera feed and scene understanding
    - MemoryLogger for XR experience logging
    - ScrollEngine for XR-triggered rituals
    - SymbolicState for XR context awareness
    """
    
    def __init__(self, config_path: str = "config/xr_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.current_session: Optional[XRSession] = None
        self.session_history: List[XRSession] = []
        self.registered_handlers: Dict[str, List[Callable]] = {}
        self.device_capabilities: Dict[str, Any] = {}
        self._initialize_subsystems()
        print("[XREngine] Core initialized.")
        
    def _load_config(self) -> Dict:
        """Load XR configuration from file or create defaults."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "default_mode": "ar",
            "enable_spatial_anchors": True,
            "enable_gesture_input": True,
            "enable_voice_in_xr": True,
            "training_module_enabled": True,
            "overlay_opacity_default": 0.85,
            "anchor_persistence": True,
            "simulation_mode": True,  # For development without hardware
            "supported_devices": ["headset", "glasses", "phone_ar", "simulated"],
            "session_auto_save": True
        }
        
        # Save default config
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
    
    def _initialize_subsystems(self):
        """Initialize XR subsystem connections."""
        self.device_capabilities = {
            "spatial_tracking": True,
            "hand_tracking": True,
            "eye_tracking": False,  # Requires specific hardware
            "passthrough": True,
            "spatial_audio": True,
            "haptic_feedback": False
        }
        
        # Register default event handlers
        self.registered_handlers = {
            "session_start": [],
            "session_end": [],
            "anchor_placed": [],
            "overlay_updated": [],
            "gesture_detected": [],
            "training_event": []
        }
        
    def start_session(self, mode: str = "ar", device_type: str = "simulated") -> XRSession:
        """
        Start a new XR session.
        
        Args:
            mode: XR mode (ar, vr, mr, passthrough)
            device_type: Device type to use
            
        Returns:
            XRSession object
        """
        # End any existing session
        if self.current_session and self.current_session.is_active:
            self.end_session()
            
        # Parse mode and device type with aliases
        mode_map = {
            "ar": XRMode.AR,
            "augmented_reality": XRMode.AR,
            "vr": XRMode.VR,
            "virtual_reality": XRMode.VR,
            "mr": XRMode.MR,
            "mixed_reality": XRMode.MR,
            "passthrough": XRMode.PASSTHROUGH,
            "inactive": XRMode.INACTIVE
        }
        device_map = {
            "headset": XRDeviceType.HEADSET,
            "glasses": XRDeviceType.GLASSES,
            "phone_ar": XRDeviceType.PHONE_AR,
            "phone": XRDeviceType.PHONE_AR,
            "projection": XRDeviceType.PROJECTION,
            "holographic": XRDeviceType.HOLOGRAPHIC,
            "simulated": XRDeviceType.SIMULATED,
            "sim": XRDeviceType.SIMULATED
        }
        
        xr_mode = mode_map.get(mode.lower().replace(" ", "_"), XRMode.AR) if mode else XRMode.AR
        xr_device = device_map.get(device_type.lower(), XRDeviceType.SIMULATED) if device_type else XRDeviceType.SIMULATED
        
        # Create new session
        session_id = f"xr_{int(time.time())}_{xr_mode.value[:2]}"
        self.current_session = XRSession(session_id, xr_mode, xr_device)
        
        print(f"[XREngine] Started {xr_mode.value} session on {xr_device.value} device.")
        self.current_session.log_event("session_started", {
            "mode": xr_mode.value,
            "device": xr_device.value
        })
        
        # Trigger handlers
        self._trigger_handlers("session_start", self.current_session)
        
        return self.current_session
    
    def end_session(self) -> Optional[Dict]:
        """End the current XR session and return summary."""
        if not self.current_session:
            print("[XREngine] No active session to end.")
            return None
            
        self.current_session.is_active = False
        self.current_session.log_event("session_ended", {
            "duration_seconds": (datetime.now() - self.current_session.started_at).total_seconds()
        })
        
        # Save session to history
        self.session_history.append(self.current_session)
        
        # Save session if configured
        if self.config.get("session_auto_save"):
            self._save_session_log(self.current_session)
            
        summary = self.current_session.to_dict()
        print(f"[XREngine] Session {self.current_session.session_id} ended.")
        
        # Trigger handlers
        self._trigger_handlers("session_end", self.current_session)
        
        self.current_session = None
        return summary
    
    def get_session_status(self) -> Dict:
        """Get current session status."""
        if not self.current_session:
            return {"status": "inactive", "session": None}
            
        return {
            "status": "active",
            "session": self.current_session.to_dict()
        }
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a callback handler for XR events."""
        if event_type not in self.registered_handlers:
            self.registered_handlers[event_type] = []
        self.registered_handlers[event_type].append(handler)
        print(f"[XREngine] Registered handler for event: {event_type}")
        
    def _trigger_handlers(self, event_type: str, data: Any):
        """Trigger all registered handlers for an event type."""
        handlers = self.registered_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"[XREngine] Handler error for {event_type}: {e}")
                
    def _save_session_log(self, session: XRSession):
        """Save session log to file."""
        os.makedirs("logs/xr_sessions", exist_ok=True)
        log_path = f"logs/xr_sessions/{session.session_id}.json"
        
        session_data = session.to_dict()
        session_data["event_log"] = session.event_log
        
        with open(log_path, "w") as f:
            json.dump(session_data, f, indent=2)
        print(f"[XREngine] Session log saved to {log_path}")
        
    def get_device_capabilities(self) -> Dict[str, Any]:
        """Get current device capabilities."""
        return self.device_capabilities.copy()
    
    def update_symbolic_state(self, state_manager) -> Dict:
        """
        Update the symbolic state with XR context.
        
        Args:
            state_manager: LAM symbolic state manager
            
        Returns:
            Updated XR state dictionary
        """
        xr_state = {
            "xr_active": self.current_session is not None,
            "xr_mode": self.current_session.mode.value if self.current_session else None,
            "xr_device": self.current_session.device_type.value if self.current_session else None,
            "anchors_placed": len(self.current_session.spatial_anchors) if self.current_session else 0,
            "overlays_active": len(self.current_session.overlays) if self.current_session else 0
        }
        
        return xr_state
    
    def process_frame(self, frame_data: Dict) -> Dict:
        """
        Process an XR frame update - used for real-time AR/VR rendering loops.
        
        Args:
            frame_data: Dictionary containing frame information
            
        Returns:
            Processed frame with augmentations
        """
        if not self.current_session:
            return {"error": "No active XR session"}
            
        # Log frame event (throttled in production)
        processed = {
            "frame_id": frame_data.get("frame_id", 0),
            "timestamp": datetime.now().isoformat(),
            "mode": self.current_session.mode.value,
            "overlays_to_render": [],
            "anchors_visible": [],
            "gesture_feedback": None
        }
        
        # In a real implementation, this would process spatial data
        # and determine what overlays to render
        
        return processed


# Utility functions for daemon integration
def create_xr_engine(config_path: str = "config/xr_config.json") -> XREngine:
    """Factory function to create XR engine instance."""
    return XREngine(config_path)


def get_xr_status(engine: Optional[XREngine]) -> str:
    """Get human-readable XR status."""
    if not engine:
        return "[XR] Engine not initialized"
    
    status = engine.get_session_status()
    if status["status"] == "inactive":
        return "[XR] No active session"
    
    session = status["session"]
    return f"[XR] Active {session['mode']} session on {session['device_type']}"
