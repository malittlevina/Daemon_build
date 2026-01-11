# Robotics Control Module

AI-native robotics control for the Prometheus Daemon, designed for a miniature companion robot that can hang on the user or follow them around.

## Overview

This module provides a complete robotics control stack:

- **Hardware Abstraction Layer (HAL)** - Clean interface to motors and sensors
- **Motion Controller** - Movement primitives and gesture sequences  
- **Robot State Manager** - Symbolic state integrated with daemon
- **Navigation Planner** - Path planning with LAM integration
- **Companion Behaviors** - High-level behavior patterns

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Prometheus Daemon                     │
├─────────────────────────────────────────────────────────┤
│  NLU Engine  │  Scroll Engine  │  LAM Planner  │ Unimind│
├─────────────────────────────────────────────────────────┤
│                    Robot Scrolls                         │
├─────────────────────────────────────────────────────────┤
│                      RobotCore                           │
├────────────┬─────────────┬─────────────┬───────────────┤
│ Companion  │ Navigation  │   Motion    │    Robot      │
│ Behaviors  │   Planner   │ Controller  │    State      │
├────────────┴─────────────┴─────────────┴───────────────┤
│              Hardware Abstraction Layer                  │
├─────────────────────────────────────────────────────────┤
│  Motors (Servos, DC)  │  Sensors (IMU, Distance, etc.) │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Simulation Mode (Development)

The robotics module runs in simulation mode by default:

```python
from robotics.robot_core import RobotCore

# Initialize in simulation mode
robot = RobotCore(simulation_mode=True)
robot.start()

# Execute commands
robot.execute_command("follow", distance=1.0)
robot.execute_command("gesture", name="wave")
robot.execute_command("navigate", target="desk")

# Get status
status = robot.get_status()
print(status)

# Shutdown
robot.stop()
```

### Daemon Integration

The robotics module is automatically integrated with the daemon when `ENABLE_ROBOTICS = True` in `main.py`.

#### Direct Robot Commands

```
robot status       - Get robot status
robot follow       - Start following user
robot stop         - Stop all movement
robot perch        - Attach to user (shoulder by default)
robot go desk      - Navigate to 'desk' location
robot home         - Navigate to home position
robot wave         - Perform wave gesture
robot calibrate    - Run calibration routine
```

#### Via Scroll Engine

```python
scrolls.invoke("robot follow")
scrolls.invoke("robot navigate", target="kitchen")
scrolls.invoke("robot gesture", name="happy")
```

## Hardware Abstraction Layer

The HAL provides a unified interface for hardware communication:

### Supported Motor Types
- DC Brushed Motors (wheels)
- Servos (head, arms, grip)
- Steppers (optional precision movement)
- Linear Actuators (optional)

### Supported Sensors
- IMU (Inertial Measurement Unit)
- Distance Sensors (Ultrasonic/IR/ToF)
- Camera
- Touch Sensors
- Force Sensors (grip feedback)
- Battery Monitor
- Encoders

### Adding Real Hardware

1. Set `simulation_mode=False` when creating RobotCore
2. Configure hardware interface in `config/robotics_config.json`
3. Implement hardware communication in `hal.py`:

```python
# Example: Serial communication with microcontroller
def _send_motor_command(self, motor_id: str, value: float) -> None:
    if self._connection:
        packet = f"M:{motor_id}:{value}\n"
        self._connection.write(packet.encode())
```

## Motion Controller

### Movement Primitives

```python
motion.move_forward(speed=0.3)
motion.turn_left(speed=1.0)
motion.stop()
motion.look_at(pan=30, tilt=15)
motion.set_grip(force=0.7)
```

### Gesture Library

Built-in gestures:
- `wave` - Friendly wave
- `nod` - Affirmative nod
- `shake_head` - Negative shake
- `look_around` - Curious look
- `happy` - Happy expression
- `sad` - Sad expression
- `curious` - Curious pose
- `attention` - Alert pose
- `sleep` - Rest pose
- `wake` - Wake up sequence

## Companion Behaviors

### Modes

| Mode | Description |
|------|-------------|
| IDLE | Stationary with ambient movements |
| FOLLOWING | Following user at set distance |
| PERCHED | Attached to user, maintaining grip |
| NAVIGATING | Moving to a destination |
| DOCKED | At charging station |

### Personality Traits

Adjustable traits that influence behavior:

- **curiosity** (0-1) - How often it looks around
- **playfulness** (0-1) - Gesture frequency
- **calmness** (0-1) - Movement smoothness
- **affection** (0-1) - User focus
- **energy** (0-1) - Activity level

```python
robot.companion.set_personality_trait("curiosity", 0.8)
```

## Navigation

### Semantic Locations

Pre-defined locations that can be navigated to by name:

```python
robot.navigation.add_semantic_location("kitchen", 4.0, 2.0)
robot.execute_command("navigate", target="kitchen")
```

### Path Planning

Simple waypoint-based navigation with obstacle avoidance.

## Future Hardware Development

### Recommended Components

**Microcontroller:**
- ESP32 (WiFi/BT, dual-core)
- Teensy 4.0 (high-speed, Arduino compatible)
- STM32F4 (industrial grade)

**Motors:**
- Micro servos (SG90, MG90S)
- N20 micro gear motors with encoders
- Linear micro actuators

**Sensors:**
- MPU6050/BNO055 IMU
- VL53L0X ToF distance sensors
- OV2640 camera module
- Capacitive touch sensors
- FSR402 force sensors

**Power:**
- LiPo 1S-2S (3.7-7.4V)
- TP4056 charging module
- Voltage monitoring

### Communication Protocol

The HAL is designed to communicate with a microcontroller using a simple serial protocol:

```
# Motor command
M:<motor_id>:<value>\n

# Sensor request
S:<sensor_id>?\n

# Sensor response
S:<sensor_id>:<type>:<value>\n
```

## Configuration

Edit `config/robotics_config.json` to customize:

- Hardware interface settings
- Motor configurations
- Sensor configurations
- Behavior parameters
- Personality traits
- Semantic locations

## Integration with Daemon Subsystems

### LAM Planner
Robot commands are parsed by the LAM planner for context-aware execution.

### Symbolic State
Robot state is synced to `lam/symbolic_state.py` for cross-system awareness.

### Emotion Engine
Companion mood syncs with the daemon's emotion engine.

### Scroll Engine
All robot commands are available as scrolls.

## Development Roadmap

- [ ] Real hardware driver implementation
- [ ] SLAM/localization integration
- [ ] Voice command integration
- [ ] Person tracking via camera
- [ ] Learning-based behavior adaptation
- [ ] Multi-robot coordination
- [ ] Wireless charging dock
