# devices/wearables/drone.py
"""
Drone Interface
===============
Interface for aerial drones.
Provides aerial observation, delivery, and surveillance capabilities.
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


class FlightMode(Enum):
    """Drone flight modes."""
    GROUNDED = "grounded"
    TAKING_OFF = "taking_off"
    HOVERING = "hovering"
    FLYING = "flying"
    LANDING = "landing"
    RETURNING = "returning"
    FOLLOWING = "following"
    ORBITING = "orbiting"
    WAYPOINT = "waypoint"
    EMERGENCY = "emergency"


class CameraMode(Enum):
    """Drone camera modes."""
    PHOTO = "photo"
    VIDEO = "video"
    TIMELAPSE = "timelapse"
    PANORAMA = "panorama"
    TRACKING = "tracking"
    THERMAL = "thermal"


@dataclass
class DronePosition:
    """Drone 3D position."""
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0  # meters above ground
    heading: float = 0.0   # degrees
    speed: float = 0.0     # m/s


@dataclass
class DroneState:
    """Current drone state."""
    flight_mode: FlightMode = FlightMode.GROUNDED
    position: DronePosition = field(default_factory=DronePosition)
    battery_level: float = 100.0
    signal_strength: int = 100
    gps_satellites: int = 0
    wind_speed: float = 0.0
    is_recording: bool = False
    camera_mode: CameraMode = CameraMode.PHOTO
    gimbal_pitch: float = 0.0  # -90 to 0 degrees
    obstacle_ahead: bool = False
    return_to_home_set: bool = False


@dataclass
class Waypoint:
    """A waypoint for drone navigation."""
    latitude: float
    longitude: float
    altitude: float
    action: str = "hover"  # hover, photo, orbit, etc.
    duration_seconds: float = 0.0


class Drone(WearableDevice):
    """
    Aerial Drone - provides bird's eye observation.
    
    Capabilities:
    - Flight: Autonomous navigation
    - Camera: Aerial photography/video
    - GPS: Precise positioning
    - Sensors: Obstacle avoidance
    - Delivery: Carry small payloads (optional)
    """
    
    DEFAULT_CAPABILITIES = [
        WearableCapability.CAMERA,
        WearableCapability.FLIGHT,
        WearableCapability.GPS,
        WearableCapability.MOTION,
        WearableCapability.WIFI,
        WearableCapability.BLUETOOTH,
    ]
    
    # Safety limits
    MAX_ALTITUDE = 120.0  # meters
    MAX_DISTANCE = 500.0  # meters from home
    MIN_BATTERY_RETURN = 20.0  # percent
    
    def __init__(self, device_id: str, name: str = "Aerial Drone"):
        super().__init__(
            device_id=device_id,
            name=name,
            wearable_type=WearableType.DRONE,
            capabilities=self.DEFAULT_CAPABILITIES
        )
        
        self.state = DroneState()
        self.home_position: Optional[DronePosition] = None
        
        # Mission
        self.waypoints: List[Waypoint] = []
        self.current_waypoint_index: int = 0
        
        # Geofence
        self.geofence_enabled = True
        self.geofence_radius = self.MAX_DISTANCE
        
        # Tracking
        self.tracking_target: Optional[str] = None
        
        print(f"[Drone] Initialized: {name}")
    
    def connect(self) -> bool:
        """Connect to the drone."""
        self.status.connection_state = ConnectionState.CONNECTING
        print(f"[Drone] Connecting to {self.name}...")
        
        time.sleep(0.5)
        
        self.status.connection_state = ConnectionState.CONNECTED
        self.status.last_sync = time.time()
        
        # Set home position
        self._set_home()
        
        print(f"[Drone] Connected to {self.name}")
        self.emit('connected', self.to_dict())
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from the drone."""
        if self.state.flight_mode != FlightMode.GROUNDED:
            print("[Drone] Warning: Drone not grounded!")
            self.land()
        
        self.status.connection_state = ConnectionState.DISCONNECTED
        print(f"[Drone] Disconnected from {self.name}")
        self.emit('disconnected', self.to_dict())
        return True
    
    def sync(self) -> Dict[str, Any]:
        """Sync state from drone."""
        self._sensor_data = {
            'flight_mode': self.state.flight_mode.value,
            'position': {
                'lat': self.state.position.latitude,
                'lon': self.state.position.longitude,
                'alt': self.state.position.altitude,
                'heading': self.state.position.heading,
                'speed': self.state.position.speed
            },
            'battery': self.state.battery_level,
            'signal': self.state.signal_strength,
            'gps_satellites': self.state.gps_satellites,
            'is_recording': self.state.is_recording,
            'camera_mode': self.state.camera_mode.value,
            'obstacle': self.state.obstacle_ahead
        }
        
        self.status.last_sync = time.time()
        self.status.battery_level = self.state.battery_level
        
        # Check battery
        self._check_battery()
        
        return self._sensor_data
    
    def _set_home(self):
        """Set home position."""
        self.home_position = DronePosition(
            latitude=self.state.position.latitude,
            longitude=self.state.position.longitude,
            altitude=0
        )
        self.state.return_to_home_set = True
        print("[Drone] Home position set")
    
    def _check_battery(self):
        """Check battery and trigger return if low."""
        if self.state.battery_level < self.MIN_BATTERY_RETURN:
            if self.state.flight_mode not in [FlightMode.GROUNDED, FlightMode.LANDING, FlightMode.RETURNING]:
                print("[Drone] Low battery! Returning to home.")
                self.emit('low_battery', {'level': self.state.battery_level})
                self.return_to_home()
    
    # ==================
    # Flight Control
    # ==================
    
    def takeoff(self, altitude: float = 10.0) -> bool:
        """Take off to specified altitude."""
        if self.state.flight_mode != FlightMode.GROUNDED:
            print("[Drone] Already airborne")
            return False
        
        altitude = min(altitude, self.MAX_ALTITUDE)
        
        self.state.flight_mode = FlightMode.TAKING_OFF
        print(f"[Drone] Taking off to {altitude}m")
        self.emit('takeoff', {'target_altitude': altitude})
        
        def complete_takeoff():
            time.sleep(3)
            self.state.position.altitude = altitude
            self.state.flight_mode = FlightMode.HOVERING
            print(f"[Drone] Hovering at {altitude}m")
            self.emit('hovering', {'altitude': altitude})
        
        threading.Thread(target=complete_takeoff, daemon=True).start()
        return True
    
    def land(self) -> bool:
        """Land the drone."""
        if self.state.flight_mode == FlightMode.GROUNDED:
            return True
        
        self.state.flight_mode = FlightMode.LANDING
        print("[Drone] Landing...")
        self.emit('landing', {})
        
        def complete_landing():
            time.sleep(3)
            self.state.position.altitude = 0
            self.state.flight_mode = FlightMode.GROUNDED
            print("[Drone] Landed")
            self.emit('landed', {})
        
        threading.Thread(target=complete_landing, daemon=True).start()
        return True
    
    def return_to_home(self) -> bool:
        """Return to home position."""
        if not self.state.return_to_home_set:
            print("[Drone] No home position set!")
            return False
        
        self.state.flight_mode = FlightMode.RETURNING
        print("[Drone] Returning to home...")
        self.emit('returning_home', {})
        
        def complete_return():
            time.sleep(5)
            if self.home_position:
                self.state.position.latitude = self.home_position.latitude
                self.state.position.longitude = self.home_position.longitude
            self.land()
        
        threading.Thread(target=complete_return, daemon=True).start()
        return True
    
    def fly_to(self, latitude: float, longitude: float, altitude: float = None) -> bool:
        """Fly to GPS coordinates."""
        if self.state.flight_mode == FlightMode.GROUNDED:
            self.takeoff()
            time.sleep(4)
        
        altitude = altitude or self.state.position.altitude
        altitude = min(altitude, self.MAX_ALTITUDE)
        
        # Check geofence
        if self.geofence_enabled:
            distance = self._calculate_distance(latitude, longitude)
            if distance > self.geofence_radius:
                print(f"[Drone] Target outside geofence ({distance:.0f}m)")
                return False
        
        self.state.flight_mode = FlightMode.FLYING
        print(f"[Drone] Flying to ({latitude}, {longitude}) at {altitude}m")
        self.emit('flying_to', {'lat': latitude, 'lon': longitude, 'alt': altitude})
        
        def complete_flight():
            time.sleep(3)
            self.state.position.latitude = latitude
            self.state.position.longitude = longitude
            self.state.position.altitude = altitude
            self.state.flight_mode = FlightMode.HOVERING
            print("[Drone] Arrived at destination")
            self.emit('arrived', {'lat': latitude, 'lon': longitude})
        
        threading.Thread(target=complete_flight, daemon=True).start()
        return True
    
    def _calculate_distance(self, lat: float, lon: float) -> float:
        """Calculate distance from home."""
        if not self.home_position:
            return 0
        
        # Simplified distance calculation
        import math
        R = 6371000  # Earth radius in meters
        dlat = math.radians(lat - self.home_position.latitude)
        dlon = math.radians(lon - self.home_position.longitude)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(self.home_position.latitude)) * math.cos(math.radians(lat)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def hover(self):
        """Hold current position."""
        if self.state.flight_mode != FlightMode.GROUNDED:
            self.state.flight_mode = FlightMode.HOVERING
            self.state.position.speed = 0
            print("[Drone] Hovering")
    
    def orbit(self, radius: float = 10.0, speed: float = 2.0):
        """Orbit around current position."""
        if self.state.flight_mode == FlightMode.GROUNDED:
            return
        
        self.state.flight_mode = FlightMode.ORBITING
        print(f"[Drone] Orbiting at {radius}m radius")
        self.emit('orbiting', {'radius': radius, 'speed': speed})
    
    # ==================
    # Camera
    # ==================
    
    def set_camera_mode(self, mode: CameraMode):
        """Set camera mode."""
        self.state.camera_mode = mode
        print(f"[Drone] Camera mode: {mode.value}")
    
    def take_photo(self) -> Dict[str, Any]:
        """Take aerial photo."""
        photo_id = f"aerial_{int(time.time())}"
        
        print(f"[Drone] Photo captured: {photo_id}")
        self.emit('photo_taken', {
            'photo_id': photo_id,
            'position': {
                'lat': self.state.position.latitude,
                'lon': self.state.position.longitude,
                'alt': self.state.position.altitude
            }
        })
        
        return {'photo_id': photo_id}
    
    def start_recording(self) -> bool:
        """Start video recording."""
        if self.state.is_recording:
            return False
        
        self.state.is_recording = True
        self.state.camera_mode = CameraMode.VIDEO
        print("[Drone] Recording started")
        self.emit('recording_started', {})
        return True
    
    def stop_recording(self) -> Dict[str, Any]:
        """Stop video recording."""
        if not self.state.is_recording:
            return {'error': 'Not recording'}
        
        self.state.is_recording = False
        print("[Drone] Recording stopped")
        self.emit('recording_stopped', {})
        return {'status': 'stopped'}
    
    def set_gimbal(self, pitch: float):
        """Set gimbal pitch (-90 to 0)."""
        self.state.gimbal_pitch = max(-90, min(0, pitch))
        print(f"[Drone] Gimbal pitch: {self.state.gimbal_pitch}°")
    
    def look_down(self):
        """Point camera straight down."""
        self.set_gimbal(-90)
    
    def look_forward(self):
        """Point camera forward."""
        self.set_gimbal(0)
    
    # ==================
    # Missions
    # ==================
    
    def add_waypoint(self, lat: float, lon: float, alt: float, action: str = "hover"):
        """Add waypoint to mission."""
        waypoint = Waypoint(
            latitude=lat,
            longitude=lon,
            altitude=min(alt, self.MAX_ALTITUDE),
            action=action
        )
        self.waypoints.append(waypoint)
        print(f"[Drone] Waypoint added: ({lat}, {lon}, {alt}m)")
    
    def clear_waypoints(self):
        """Clear all waypoints."""
        self.waypoints.clear()
        self.current_waypoint_index = 0
        print("[Drone] Waypoints cleared")
    
    def start_mission(self) -> bool:
        """Start waypoint mission."""
        if not self.waypoints:
            print("[Drone] No waypoints set")
            return False
        
        self.state.flight_mode = FlightMode.WAYPOINT
        self.current_waypoint_index = 0
        
        print(f"[Drone] Starting mission with {len(self.waypoints)} waypoints")
        self.emit('mission_started', {'waypoints': len(self.waypoints)})
        
        def execute_mission():
            for i, waypoint in enumerate(self.waypoints):
                if self.state.flight_mode != FlightMode.WAYPOINT:
                    break
                
                self.current_waypoint_index = i
                self.fly_to(waypoint.latitude, waypoint.longitude, waypoint.altitude)
                time.sleep(3)
                
                if waypoint.action == "photo":
                    self.take_photo()
                elif waypoint.action == "orbit":
                    self.orbit()
                    time.sleep(waypoint.duration_seconds or 10)
            
            print("[Drone] Mission complete")
            self.emit('mission_complete', {})
            self.return_to_home()
        
        threading.Thread(target=execute_mission, daemon=True).start()
        return True
    
    def abort_mission(self):
        """Abort current mission."""
        if self.state.flight_mode == FlightMode.WAYPOINT:
            print("[Drone] Mission aborted")
            self.emit('mission_aborted', {})
            self.hover()
    
    # ==================
    # Follow/Track
    # ==================
    
    def follow_target(self, target_id: str = "user"):
        """Follow and track a target."""
        self.state.flight_mode = FlightMode.FOLLOWING
        self.tracking_target = target_id
        self.state.camera_mode = CameraMode.TRACKING
        
        print(f"[Drone] Following: {target_id}")
        self.emit('following', {'target': target_id})
    
    def stop_following(self):
        """Stop following target."""
        if self.state.flight_mode == FlightMode.FOLLOWING:
            self.tracking_target = None
            self.hover()
            print("[Drone] Stopped following")
    
    # ==================
    # Commands
    # ==================
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send command to drone."""
        params = params or {}
        
        if command == 'takeoff':
            return self.takeoff(params.get('altitude', 10))
        elif command == 'land':
            return self.land()
        elif command == 'return_home':
            return self.return_to_home()
        elif command == 'fly_to':
            return self.fly_to(
                params.get('lat', 0),
                params.get('lon', 0),
                params.get('alt')
            )
        elif command == 'hover':
            self.hover()
            return True
        elif command == 'photo':
            self.take_photo()
            return True
        elif command == 'record':
            return self.start_recording()
        elif command == 'stop_record':
            self.stop_recording()
            return True
        elif command == 'follow':
            self.follow_target(params.get('target', 'user'))
            return True
        elif command == 'orbit':
            self.orbit(params.get('radius', 10))
            return True
        elif command == 'gimbal':
            self.set_gimbal(params.get('pitch', 0))
            return True
        elif command == 'mission_start':
            return self.start_mission()
        elif command == 'mission_abort':
            self.abort_mission()
            return True
        
        return False
