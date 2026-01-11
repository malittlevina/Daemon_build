from __future__ import annotations

from abc import ABC, abstractmethod

from robotics.types import RobotCapabilities, RobotCommand, RobotTelemetry


class RobotDriver(ABC):
    """
    Hardware abstraction for robotics control.
    Implementations: simulation, ROS2, serial MCU, BLE, etc.
    """

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def capabilities(self) -> RobotCapabilities: ...

    @abstractmethod
    def execute(self, command: RobotCommand) -> str:
        """
        Execute a command and return a short human-readable result.
        Should raise on irrecoverable driver errors.
        """

    @abstractmethod
    def telemetry(self) -> RobotTelemetry: ...

