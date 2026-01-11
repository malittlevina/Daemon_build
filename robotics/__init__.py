# robotics/__init__.py
"""
Robotics Control Module for Prometheus Daemon

This module provides AI-native robotics control capabilities for companion robots.
Designed for a miniature robot that can hang on the user or follow them around.

Architecture:
- Hardware Abstraction Layer (HAL): Abstracts motor/sensor interfaces
- Motion Controller: Movement primitives and kinematics
- Robot State: Symbolic state management for the robot
- Navigation Planner: Intelligent path planning via LAM
- Companion Behaviors: High-level behavior patterns
"""

from robotics.robot_core import RobotCore
from robotics.hal import HardwareAbstractionLayer
from robotics.motion_controller import MotionController
from robotics.robot_state import RobotState
from robotics.navigation import NavigationPlanner
from robotics.companion import CompanionBehaviors

__all__ = [
    "RobotCore",
    "HardwareAbstractionLayer", 
    "MotionController",
    "RobotState",
    "NavigationPlanner",
    "CompanionBehaviors"
]
