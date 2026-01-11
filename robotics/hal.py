# robotics/hal.py
"""
Hardware Abstraction Layer (HAL) for Robotics Control.

This module provides a clean abstraction over hardware interfaces,
allowing the robotics code to work in simulation mode during development
and seamlessly switch to real hardware when available.

Supported Hardware Interfaces (Future):
- Serial/UART for microcontroller communication
- I2C for sensor arrays
- PWM for motor control
- GPIO for discrete signals
- USB for higher-bandwidth sensors
"""

import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
import math
import random


class HardwareType(Enum):
    """Types of hardware interfaces."""
    SIMULATION = "simulation"
    SERIAL = "serial"
    I2C = "i2c"
    SPI = "spi"
    GPIO = "gpio"
    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"


class MotorType(Enum):
    """Types of motors supported."""
    SERVO = "servo"
    DC_BRUSHED = "dc_brushed"
    DC_BRUSHLESS = "dc_brushless"
    STEPPER = "stepper"
    LINEAR_ACTUATOR = "linear_actuator"


class SensorType(Enum):
    """Types of sensors supported."""
    IMU = "imu"  # Inertial Measurement Unit
    DISTANCE = "distance"  # Ultrasonic/IR/ToF
    CAMERA = "camera"
    TOUCH = "touch"
    FORCE = "force"
    TEMPERATURE = "temperature"
    BATTERY = "battery"
    ENCODER = "encoder"
    GPS = "gps"
    LIDAR = "lidar"


@dataclass
class MotorConfig:
    """Configuration for a motor."""
    motor_id: str
    motor_type: MotorType
    min_value: float = -1.0
    max_value: float = 1.0
    inverted: bool = False
    home_position: float = 0.0
    max_velocity: float = 1.0  # units per second
    acceleration: float = 2.0  # units per second^2


@dataclass
class SensorConfig:
    """Configuration for a sensor."""
    sensor_id: str
    sensor_type: SensorType
    update_rate_hz: float = 50.0
    filters: List[str] = field(default_factory=list)


@dataclass
class SensorReading:
    """A timestamped sensor reading."""
    sensor_id: str
    sensor_type: SensorType
    value: Any
    timestamp: float
    valid: bool = True


class HardwareAbstractionLayer:
    """
    Hardware Abstraction Layer for robotics control.
    
    Provides unified interface for:
    - Motor control (servos, DC motors, steppers)
    - Sensor reading (IMU, distance, camera, etc.)
    - Battery monitoring
    - Hardware diagnostics
    """
    
    def __init__(self, simulation: bool = True):
        """
        Initialize the HAL.
        
        Args:
            simulation: If True, simulate all hardware
        """
        self.simulation = simulation
        self.initialized = False
        
        # Motor state
        self.motors: Dict[str, MotorConfig] = {}
        self.motor_positions: Dict[str, float] = {}
        self.motor_velocities: Dict[str, float] = {}
        self.motor_targets: Dict[str, float] = {}
        
        # Sensor state
        self.sensors: Dict[str, SensorConfig] = {}
        self.sensor_readings: Dict[str, SensorReading] = {}
        
        # Hardware connection
        self._connection = None
        self._last_sensor_update = 0.0
        
        # Default robot configuration for companion robot
        self._configure_default_robot()
        
        print(f"[HAL] Initialized in {'simulation' if simulation else 'hardware'} mode")
    
    def _configure_default_robot(self) -> None:
        """Configure default motors and sensors for a companion robot."""
        # Movement motors
        self.register_motor(MotorConfig(
            motor_id="wheel_left",
            motor_type=MotorType.DC_BRUSHED,
            min_value=-1.0,
            max_value=1.0
        ))
        self.register_motor(MotorConfig(
            motor_id="wheel_right",
            motor_type=MotorType.DC_BRUSHED,
            min_value=-1.0,
            max_value=1.0
        ))
        
        # Head/Neck servos for expression
        self.register_motor(MotorConfig(
            motor_id="neck_pan",
            motor_type=MotorType.SERVO,
            min_value=-90.0,
            max_value=90.0,
            home_position=0.0
        ))
        self.register_motor(MotorConfig(
            motor_id="neck_tilt",
            motor_type=MotorType.SERVO,
            min_value=-30.0,
            max_value=60.0,
            home_position=0.0
        ))
        
        # Grip mechanism for perching
        self.register_motor(MotorConfig(
            motor_id="grip_left",
            motor_type=MotorType.SERVO,
            min_value=0.0,
            max_value=90.0,
            home_position=45.0
        ))
        self.register_motor(MotorConfig(
            motor_id="grip_right",
            motor_type=MotorType.SERVO,
            min_value=0.0,
            max_value=90.0,
            home_position=45.0
        ))
        
        # Arm/wing for gestures (optional expansion)
        self.register_motor(MotorConfig(
            motor_id="arm_left",
            motor_type=MotorType.SERVO,
            min_value=-45.0,
            max_value=180.0,
            home_position=0.0
        ))
        self.register_motor(MotorConfig(
            motor_id="arm_right",
            motor_type=MotorType.SERVO,
            min_value=-45.0,
            max_value=180.0,
            home_position=0.0
        ))
        
        # Sensors
        self.register_sensor(SensorConfig(
            sensor_id="imu_main",
            sensor_type=SensorType.IMU,
            update_rate_hz=100.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="distance_front",
            sensor_type=SensorType.DISTANCE,
            update_rate_hz=20.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="distance_left",
            sensor_type=SensorType.DISTANCE,
            update_rate_hz=20.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="distance_right",
            sensor_type=SensorType.DISTANCE,
            update_rate_hz=20.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="camera_main",
            sensor_type=SensorType.CAMERA,
            update_rate_hz=30.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="battery",
            sensor_type=SensorType.BATTERY,
            update_rate_hz=1.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="touch_head",
            sensor_type=SensorType.TOUCH,
            update_rate_hz=50.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="grip_force_left",
            sensor_type=SensorType.FORCE,
            update_rate_hz=50.0
        ))
        self.register_sensor(SensorConfig(
            sensor_id="grip_force_right",
            sensor_type=SensorType.FORCE,
            update_rate_hz=50.0
        ))
    
    def register_motor(self, config: MotorConfig) -> None:
        """Register a motor with the HAL."""
        self.motors[config.motor_id] = config
        self.motor_positions[config.motor_id] = config.home_position
        self.motor_velocities[config.motor_id] = 0.0
        self.motor_targets[config.motor_id] = config.home_position
    
    def register_sensor(self, config: SensorConfig) -> None:
        """Register a sensor with the HAL."""
        self.sensors[config.sensor_id] = config
        self.sensor_readings[config.sensor_id] = SensorReading(
            sensor_id=config.sensor_id,
            sensor_type=config.sensor_type,
            value=self._get_default_sensor_value(config.sensor_type),
            timestamp=time.time(),
            valid=True
        )
    
    def _get_default_sensor_value(self, sensor_type: SensorType) -> Any:
        """Get default value for a sensor type."""
        defaults = {
            SensorType.IMU: {"accel": [0, 0, 9.81], "gyro": [0, 0, 0], "orientation": [0, 0, 0]},
            SensorType.DISTANCE: 1.0,  # meters
            SensorType.CAMERA: None,
            SensorType.TOUCH: False,
            SensorType.FORCE: 0.0,
            SensorType.TEMPERATURE: 25.0,
            SensorType.BATTERY: {"voltage": 12.0, "percent": 100.0, "charging": False},
            SensorType.ENCODER: 0,
            SensorType.GPS: {"lat": 0.0, "lon": 0.0, "alt": 0.0},
            SensorType.LIDAR: []
        }
        return defaults.get(sensor_type, None)
    
    def initialize(self) -> bool:
        """
        Initialize hardware connections.
        
        Returns:
            True if initialization successful
        """
        if self.initialized:
            return True
        
        try:
            if self.simulation:
                print("[HAL] Simulation mode - no hardware to initialize")
            else:
                # Future: Initialize real hardware connections
                # self._connection = serial.Serial(...)
                print("[HAL] Initializing hardware connections...")
                # Placeholder for real hardware init
            
            self.initialized = True
            print("[HAL] Hardware initialized successfully")
            return True
            
        except Exception as e:
            print(f"[HAL] Initialization failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown hardware connections safely."""
        if not self.initialized:
            return
        
        # Move all motors to home position
        for motor_id, config in self.motors.items():
            self.motor_targets[motor_id] = config.home_position
        
        # Wait for motors to reach home
        time.sleep(0.5)
        
        # Stop all motors
        for motor_id in self.motors:
            self.motor_velocities[motor_id] = 0.0
        
        if self._connection:
            self._connection.close()
            self._connection = None
        
        self.initialized = False
        print("[HAL] Hardware shutdown complete")
    
    def set_motor(self, motor_id: str, value: float) -> bool:
        """
        Set motor target position/velocity.
        
        Args:
            motor_id: Motor identifier
            value: Target value (interpretation depends on motor type)
            
        Returns:
            True if command accepted
        """
        if motor_id not in self.motors:
            print(f"[HAL] Unknown motor: {motor_id}")
            return False
        
        config = self.motors[motor_id]
        
        # Clamp to valid range
        clamped = max(config.min_value, min(config.max_value, value))
        if config.inverted:
            clamped = config.max_value - (clamped - config.min_value)
        
        self.motor_targets[motor_id] = clamped
        return True
    
    def get_motor_position(self, motor_id: str) -> Optional[float]:
        """Get current motor position."""
        return self.motor_positions.get(motor_id)
    
    def update_sensors(self) -> None:
        """Update all sensor readings."""
        current_time = time.time()
        
        for sensor_id, config in self.sensors.items():
            period = 1.0 / config.update_rate_hz
            last_reading = self.sensor_readings[sensor_id]
            
            if current_time - last_reading.timestamp >= period:
                if self.simulation:
                    value = self._simulate_sensor(sensor_id, config)
                else:
                    value = self._read_real_sensor(sensor_id, config)
                
                self.sensor_readings[sensor_id] = SensorReading(
                    sensor_id=sensor_id,
                    sensor_type=config.sensor_type,
                    value=value,
                    timestamp=current_time,
                    valid=True
                )
        
        self._last_sensor_update = current_time
    
    def _simulate_sensor(self, sensor_id: str, config: SensorConfig) -> Any:
        """Generate simulated sensor values."""
        sensor_type = config.sensor_type
        
        if sensor_type == SensorType.IMU:
            # Simulate slight movement noise
            return {
                "accel": [
                    random.gauss(0, 0.1),
                    random.gauss(0, 0.1),
                    9.81 + random.gauss(0, 0.05)
                ],
                "gyro": [
                    random.gauss(0, 0.01),
                    random.gauss(0, 0.01),
                    random.gauss(0, 0.01)
                ],
                "orientation": [
                    random.gauss(0, 1),
                    random.gauss(0, 1),
                    random.gauss(0, 1)
                ]
            }
        elif sensor_type == SensorType.DISTANCE:
            # Simulate varying distance
            base = 1.0
            if "front" in sensor_id:
                base = 1.5
            return max(0.05, base + random.gauss(0, 0.1))
        elif sensor_type == SensorType.BATTERY:
            # Slowly decreasing battery
            last = self.sensor_readings[sensor_id].value
            percent = max(0, last["percent"] - 0.001)
            return {
                "voltage": 11.0 + (percent / 100.0) * 1.5,
                "percent": percent,
                "charging": False
            }
        elif sensor_type == SensorType.TOUCH:
            return random.random() < 0.01  # Occasional touch
        elif sensor_type == SensorType.FORCE:
            return max(0, random.gauss(0.5, 0.1))
        else:
            return self._get_default_sensor_value(sensor_type)
    
    def _read_real_sensor(self, sensor_id: str, config: SensorConfig) -> Any:
        """Read from real hardware sensor."""
        # Future implementation for real hardware
        # This would communicate with microcontroller via serial/I2C
        return self._get_default_sensor_value(config.sensor_type)
    
    def update_actuators(self) -> None:
        """Update actuator outputs (move motors toward targets)."""
        dt = 0.02  # Assume 50Hz update rate
        
        for motor_id, config in self.motors.items():
            current = self.motor_positions[motor_id]
            target = self.motor_targets[motor_id]
            
            # Simple velocity-limited movement
            error = target - current
            max_step = config.max_velocity * dt
            
            if abs(error) <= max_step:
                self.motor_positions[motor_id] = target
                self.motor_velocities[motor_id] = 0.0
            else:
                step = max_step if error > 0 else -max_step
                self.motor_positions[motor_id] = current + step
                self.motor_velocities[motor_id] = step / dt
            
            if self.simulation:
                # In simulation, position updates happen in memory
                pass
            else:
                # Future: Send commands to real hardware
                self._send_motor_command(motor_id, self.motor_positions[motor_id])
    
    def _send_motor_command(self, motor_id: str, value: float) -> None:
        """Send motor command to hardware."""
        # Future implementation
        pass
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """Get all current sensor readings."""
        return {
            sensor_id: {
                "type": reading.sensor_type.value,
                "value": reading.value,
                "timestamp": reading.timestamp,
                "valid": reading.valid
            }
            for sensor_id, reading in self.sensor_readings.items()
        }
    
    def get_motor_data(self) -> Dict[str, Any]:
        """Get all current motor states."""
        return {
            motor_id: {
                "type": config.motor_type.value,
                "position": self.motor_positions[motor_id],
                "velocity": self.motor_velocities[motor_id],
                "target": self.motor_targets[motor_id]
            }
            for motor_id, config in self.motors.items()
        }
    
    def home_all_motors(self) -> None:
        """Move all motors to home position."""
        for motor_id, config in self.motors.items():
            self.motor_targets[motor_id] = config.home_position
        print("[HAL] Homing all motors")
    
    def emergency_stop(self) -> None:
        """Emergency stop all motors."""
        for motor_id in self.motors:
            self.motor_targets[motor_id] = self.motor_positions[motor_id]
            self.motor_velocities[motor_id] = 0.0
        print("[HAL] Emergency stop activated")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get hardware diagnostics."""
        battery = self.sensor_readings.get("battery")
        return {
            "initialized": self.initialized,
            "simulation": self.simulation,
            "motor_count": len(self.motors),
            "sensor_count": len(self.sensors),
            "battery_percent": battery.value["percent"] if battery else None,
            "last_sensor_update": self._last_sensor_update,
            "motors_at_home": all(
                abs(self.motor_positions[mid] - config.home_position) < 0.1
                for mid, config in self.motors.items()
            )
        }
