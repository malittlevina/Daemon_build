from __future__ import annotations

from datetime import datetime, timezone

from robotics.drivers.base import RobotDriver
from robotics.types import RobotCapabilities, RobotCommand, RobotTelemetry


class SimulationDriver(RobotDriver):
    """
    A zero-dependency driver that simulates a tiny follower robot.
    Useful for developing the daemon-side command/control before hardware exists.
    """

    def __init__(self) -> None:
        self._connected = False
        self._caps = RobotCapabilities(mobility=True, follow_mode=True, stop=True)
        self._telemetry = RobotTelemetry(status="disconnected", mode="idle")

    def connect(self) -> None:
        self._connected = True
        self._telemetry.status = "connected"
        self._telemetry.extra["connected_at"] = datetime.now(timezone.utc).isoformat()

    def disconnect(self) -> None:
        self._connected = False
        self._telemetry.status = "disconnected"
        self._telemetry.mode = "idle"

    def is_connected(self) -> bool:
        return self._connected

    def capabilities(self) -> RobotCapabilities:
        return self._caps

    def execute(self, command: RobotCommand) -> str:
        name = command.name.lower().strip()
        if name == "stop":
            self._telemetry.mode = "idle"
            self._telemetry.status = "stopped"
            return "Robot stopped."

        if name == "follow":
            if not self._caps.follow_mode:
                return "Follow mode not supported by this driver."
            target = str(command.params.get("target", "user"))
            self._telemetry.mode = "follow"
            self._telemetry.status = "following"
            self._telemetry.extra["follow_target"] = target
            return f"Robot now following: {target}."

        if name == "move":
            if not self._caps.mobility:
                return "Mobility not supported by this driver."
            direction = str(command.params.get("direction", "forward")).lower()
            distance_m = float(command.params.get("distance_m", 0.25))

            if direction == "forward":
                self._telemetry.y_m += distance_m
            elif direction == "backward":
                self._telemetry.y_m -= distance_m
            elif direction == "left":
                self._telemetry.x_m -= distance_m
            elif direction == "right":
                self._telemetry.x_m += distance_m
            else:
                return f"Unknown move direction: {direction}"

            self._telemetry.status = "moved"
            self._telemetry.mode = "manual"
            return f"Moved {direction} {distance_m:.2f}m (sim)."

        return f"Unknown command: {command.name}"

    def telemetry(self) -> RobotTelemetry:
        return self._telemetry

