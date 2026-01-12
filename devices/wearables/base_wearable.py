# devices/wearables/base_wearable.py
"""
Base Wearable Device Interface
==============================
Abstract base for all wearable and companion devices.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import time
import threading


class WearableType(Enum):
    """Types of wearable/companion devices."""
    RING = "ring"
    GLASSES = "glasses"
    WATCH = "watch"
    EARBUDS = "earbuds"
    PENDANT = "pendant"
    ROBOT = "robot"
    DRONE = "drone"
    VEHICLE = "vehicle"


class WearableCapability(Enum):
    """Capabilities a wearable can have."""
    # Input/Sensing
    HEART_RATE = "heart_rate"
    BLOOD_OXYGEN = "blood_oxygen"
    TEMPERATURE = "temperature"
    MOTION = "motion"
    GESTURE = "gesture"
    TOUCH = "touch"
    PRESSURE = "pressure"
    GPS = "gps"
    MICROPHONE = "microphone"
    CAMERA = "camera"
    LIDAR = "lidar"
    DEPTH_CAMERA = "depth_camera"
    
    # Output/Feedback
    HAPTIC = "haptic"
    SPEAKER = "speaker"
    DISPLAY = "display"
    AR_OVERLAY = "ar_overlay"
    LED = "led"
    
    # Movement
    MOBILITY = "mobility"
    FLIGHT = "flight"
    MANIPULATION = "manipulation"
    
    # Communication
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    CELLULAR = "cellular"
    NFC = "nfc"


class ConnectionState(Enum):
    """Connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PAIRED = "paired"
    ERROR = "error"


@dataclass
class WearableStatus:
    """Status of a wearable device."""
    battery_level: float = 100.0  # 0-100
    is_worn: bool = False
    signal_strength: int = 0  # dBm
    connection_state: ConnectionState = ConnectionState.DISCONNECTED
    last_sync: Optional[float] = None
    firmware_version: Optional[str] = None
    error_message: Optional[str] = None


class WearableDevice(ABC):
    """
    Abstract base class for wearable devices.
    
    Each wearable provides sensory input to the daemon and
    can receive commands for output/feedback.
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        wearable_type: WearableType,
        capabilities: List[WearableCapability]
    ):
        self.device_id = device_id
        self.name = name
        self.wearable_type = wearable_type
        self.capabilities = capabilities
        self.status = WearableStatus()
        
        # Event callbacks
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Data streams
        self._sensor_data: Dict[str, Any] = {}
        self._streaming = False
        self._stream_thread: Optional[threading.Thread] = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the device."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the device."""
        pass
    
    @abstractmethod
    def sync(self) -> Dict[str, Any]:
        """Sync data from the device."""
        pass
    
    def has_capability(self, capability: WearableCapability) -> bool:
        """Check if device has a capability."""
        return capability in self.capabilities
    
    def on(self, event: str, handler: Callable):
        """Register event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def emit(self, event: str, data: Any = None):
        """Emit an event to handlers."""
        for handler in self._event_handlers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                print(f"[{self.name}] Event handler error: {e}")
    
    def get_sensor_data(self, sensor: str = None) -> Any:
        """Get sensor data."""
        if sensor:
            return self._sensor_data.get(sensor)
        return self._sensor_data
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send a command to the device."""
        # Override in subclasses
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize device info."""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'type': self.wearable_type.value,
            'capabilities': [c.value for c in self.capabilities],
            'status': {
                'battery': self.status.battery_level,
                'connection': self.status.connection_state.value,
                'is_worn': self.status.is_worn
            }
        }
