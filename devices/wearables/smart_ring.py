# devices/wearables/smart_ring.py
"""
Smart Ring Interface
====================
Interface for smart ring devices (like Oura, RingConn, etc.)
Provides biometric data and gesture input to the daemon.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .base_wearable import (
    WearableDevice, WearableType, WearableCapability,
    ConnectionState, WearableStatus
)


@dataclass
class BiometricReading:
    """Biometric data from the ring."""
    heart_rate: Optional[int] = None        # BPM
    hrv: Optional[float] = None             # Heart rate variability (ms)
    blood_oxygen: Optional[float] = None    # SpO2 percentage
    skin_temperature: Optional[float] = None # Celsius
    steps: int = 0
    calories: int = 0
    timestamp: float = 0.0


@dataclass
class GestureEvent:
    """Gesture detected by the ring."""
    gesture_type: str  # tap, double_tap, swipe, hold, pinch
    intensity: float = 1.0
    duration_ms: float = 0.0
    timestamp: float = 0.0


class SmartRing(WearableDevice):
    """
    Smart Ring - worn on finger for continuous biometric monitoring
    and gesture input.
    
    Capabilities:
    - Heart rate, HRV, SpO2 monitoring
    - Skin temperature
    - Motion/activity tracking
    - Gesture recognition (tap, swipe, etc.)
    - Haptic feedback (vibration)
    - NFC for payments/access
    """
    
    DEFAULT_CAPABILITIES = [
        WearableCapability.HEART_RATE,
        WearableCapability.BLOOD_OXYGEN,
        WearableCapability.TEMPERATURE,
        WearableCapability.MOTION,
        WearableCapability.GESTURE,
        WearableCapability.HAPTIC,
        WearableCapability.NFC,
        WearableCapability.BLUETOOTH,
    ]
    
    # Gesture patterns
    GESTURES = {
        'single_tap': 'Acknowledge/Select',
        'double_tap': 'Activate/Confirm',
        'triple_tap': 'Emergency/Cancel',
        'swipe_up': 'Next/Increase',
        'swipe_down': 'Previous/Decrease',
        'hold': 'Context menu/Listen',
        'pinch': 'Capture/Screenshot',
    }
    
    def __init__(self, device_id: str, name: str = "Smart Ring"):
        super().__init__(
            device_id=device_id,
            name=name,
            wearable_type=WearableType.RING,
            capabilities=self.DEFAULT_CAPABILITIES
        )
        
        # Biometric data
        self.current_reading = BiometricReading()
        self.reading_history: List[BiometricReading] = []
        
        # State
        self._is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        print(f"[SmartRing] Initialized: {name}")
    
    def connect(self) -> bool:
        """Connect to the ring via Bluetooth."""
        self.status.connection_state = ConnectionState.CONNECTING
        print(f"[SmartRing] Connecting to {self.name}...")
        
        # In production, this would use bleak to connect to BLE device
        # For now, simulate connection
        time.sleep(0.5)
        
        self.status.connection_state = ConnectionState.CONNECTED
        self.status.last_sync = time.time()
        print(f"[SmartRing] Connected to {self.name}")
        
        self.emit('connected', self.to_dict())
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from the ring."""
        self.stop_monitoring()
        self.status.connection_state = ConnectionState.DISCONNECTED
        print(f"[SmartRing] Disconnected from {self.name}")
        self.emit('disconnected', self.to_dict())
        return True
    
    def sync(self) -> Dict[str, Any]:
        """Sync data from the ring."""
        if self.status.connection_state != ConnectionState.CONNECTED:
            return {'error': 'Not connected'}
        
        # In production, read from BLE characteristics
        # Simulate reading
        self.current_reading = BiometricReading(
            heart_rate=72,
            hrv=45.0,
            blood_oxygen=98.0,
            skin_temperature=36.5,
            steps=self.current_reading.steps + 10,
            calories=self.current_reading.calories + 5,
            timestamp=time.time()
        )
        
        self.reading_history.append(self.current_reading)
        if len(self.reading_history) > 1000:
            self.reading_history = self.reading_history[-500:]
        
        self._sensor_data = {
            'heart_rate': self.current_reading.heart_rate,
            'hrv': self.current_reading.hrv,
            'blood_oxygen': self.current_reading.blood_oxygen,
            'temperature': self.current_reading.skin_temperature,
            'steps': self.current_reading.steps,
            'calories': self.current_reading.calories,
        }
        
        self.status.last_sync = time.time()
        self.emit('sync', self._sensor_data)
        
        return self._sensor_data
    
    def start_monitoring(self, interval_seconds: float = 60.0):
        """Start continuous biometric monitoring."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        
        def monitor_loop():
            while self._is_monitoring:
                self.sync()
                self._check_alerts()
                time.sleep(interval_seconds)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[SmartRing] Monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self._is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        print("[SmartRing] Monitoring stopped")
    
    def _check_alerts(self):
        """Check for health alerts."""
        if self.current_reading.heart_rate:
            if self.current_reading.heart_rate > 120:
                self.emit('alert', {
                    'type': 'high_heart_rate',
                    'value': self.current_reading.heart_rate,
                    'message': 'Elevated heart rate detected'
                })
            elif self.current_reading.heart_rate < 50:
                self.emit('alert', {
                    'type': 'low_heart_rate',
                    'value': self.current_reading.heart_rate,
                    'message': 'Low heart rate detected'
                })
        
        if self.current_reading.blood_oxygen and self.current_reading.blood_oxygen < 95:
            self.emit('alert', {
                'type': 'low_oxygen',
                'value': self.current_reading.blood_oxygen,
                'message': 'Blood oxygen below normal'
            })
    
    def detect_gesture(self, gesture_type: str) -> GestureEvent:
        """Process a detected gesture."""
        gesture = GestureEvent(
            gesture_type=gesture_type,
            timestamp=time.time()
        )
        
        self.emit('gesture', {
            'type': gesture_type,
            'description': self.GESTURES.get(gesture_type, 'Unknown gesture'),
            'timestamp': gesture.timestamp
        })
        
        return gesture
    
    def vibrate(self, pattern: str = 'short', intensity: float = 1.0) -> bool:
        """Send haptic feedback."""
        if not self.has_capability(WearableCapability.HAPTIC):
            return False
        
        patterns = {
            'short': [100],
            'long': [500],
            'double': [100, 100, 100],
            'sos': [100, 100, 100, 300, 300, 300, 100, 100, 100],
            'success': [100, 50, 200],
            'error': [200, 100, 200, 100, 200],
        }
        
        vibration = patterns.get(pattern, [100])
        print(f"[SmartRing] Vibrating: {pattern} ({vibration})")
        
        # In production, send to device via BLE
        return True
    
    def read_nfc(self) -> Optional[Dict[str, Any]]:
        """Read NFC tag with the ring."""
        if not self.has_capability(WearableCapability.NFC):
            return None
        
        # In production, this would trigger NFC read
        print("[SmartRing] NFC read initiated...")
        return None
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health data summary."""
        if not self.reading_history:
            return {'error': 'No data available'}
        
        heart_rates = [r.heart_rate for r in self.reading_history if r.heart_rate]
        
        return {
            'current': {
                'heart_rate': self.current_reading.heart_rate,
                'blood_oxygen': self.current_reading.blood_oxygen,
                'temperature': self.current_reading.skin_temperature,
            },
            'today': {
                'steps': self.current_reading.steps,
                'calories': self.current_reading.calories,
                'avg_heart_rate': sum(heart_rates) / len(heart_rates) if heart_rates else None,
            },
            'readings_count': len(self.reading_history)
        }
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send command to the ring."""
        if command == 'vibrate':
            return self.vibrate(
                pattern=params.get('pattern', 'short') if params else 'short',
                intensity=params.get('intensity', 1.0) if params else 1.0
            )
        elif command == 'read_nfc':
            self.read_nfc()
            return True
        elif command == 'sync':
            self.sync()
            return True
        return False
