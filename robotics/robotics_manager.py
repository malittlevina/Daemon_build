from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Optional

from memory_tree.memory_logger import log_memory
from robotics.drivers.simulated import SimulationDriver
from robotics.safety import RoboticsSafetyPolicy
from robotics.types import RobotCommand


class RoboticsManager:
    """
    Daemon-facing robotics control surface.
    - Manages arming state and safety policy
    - Owns a driver instance (simulation now, real hardware later)
    """

    def __init__(self) -> None:
        self._armed = False
        self._policy = RoboticsSafetyPolicy()
        self._driver = self._load_driver()
        try:
            self._driver.connect()
        except Exception:
            # Driver connect failure shouldn't crash daemon
            pass

    def _load_driver(self):
        # Future: read a richer config and dynamically load driver plugins.
        cfg_path = os.environ.get("ROBOTICS_CONFIG", "config/robotics.json")
        driver_name = "simulation"
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r") as f:
                    cfg = json.load(f)
                driver_name = str(cfg.get("driver", "simulation")).lower()
            except Exception:
                driver_name = "simulation"

        # Only simulation is implemented in this build; stubs can be added later.
        if driver_name != "simulation":
            driver_name = "simulation"
        return SimulationDriver()

    def arm(self) -> str:
        self._armed = True
        log_memory("Robotics armed", context={"subsystem": "robotics"})
        return "Robotics armed (motion enabled)."

    def disarm(self) -> str:
        self._armed = False
        log_memory("Robotics disarmed", context={"subsystem": "robotics"})
        return "Robotics disarmed (motion disabled)."

    def status(self) -> str:
        t = self._driver.telemetry()
        caps = self._driver.capabilities()
        return (
            f"Robot status: {t.status} | mode={t.mode} | armed={self._armed} | "
            f"pos=({t.x_m:.2f},{t.y_m:.2f})m | battery={t.battery_pct:.0f}% | "
            f"caps(mobility={caps.mobility}, follow={caps.follow_mode})"
        )

    def execute(self, command: RobotCommand) -> str:
        allowed, reason = self._policy.evaluate(command, armed=self._armed)
        if not allowed:
            return reason or "Command blocked by safety policy."

        result = self._driver.execute(command)
        log_memory(
            "Robotics command executed",
            context={
                "subsystem": "robotics",
                "command": command.name,
                "params": command.params,
                "source": command.source,
                "result": result,
            },
        )
        return result

    def handle_text_command(self, text: str, *, source: str = "unknown") -> Optional[str]:
        """
        Return a string response if this looks like a robotics command; otherwise None.
        Recognizes safe, explicit prefixes (e.g. 'robot ...').
        """
        raw = (text or "").strip()
        if not raw:
            return None

        lower = raw.lower()
        if not (lower.startswith("robot") or lower.startswith("bot")):
            return None

        # Normalize: "robot: status" -> "robot status"
        lower = re.sub(r"^robot\s*:\s*", "robot ", lower)
        lower = re.sub(r"^bot\s*:\s*", "bot ", lower)

        tokens = lower.split()
        if len(tokens) == 1:
            return self.status()

        verb = tokens[1]
        if verb in {"arm", "enable"}:
            return self.arm()
        if verb in {"disarm", "disable"}:
            return self.disarm()
        if verb in {"status", "state"}:
            return self.status()
        if verb in {"stop", "halt"}:
            return self.execute(
                RobotCommand(
                    name="stop",
                    params={},
                    source=source,
                    timestamp_utc=datetime.now(timezone.utc).isoformat(),
                )
            )
        if verb in {"follow"}:
            # "robot follow me" / "robot follow user"
            target = "user"
            if len(tokens) >= 3:
                target = tokens[2]
                if target == "me":
                    target = "user"
            return self.execute(
                RobotCommand(
                    name="follow",
                    params={"target": target},
                    source=source,
                    timestamp_utc=datetime.now(timezone.utc).isoformat(),
                )
            )
        if verb in {"move", "go"}:
            # "robot move forward 0.5"
            direction = "forward"
            distance_m = 0.25
            if len(tokens) >= 3:
                direction = tokens[2]
            if len(tokens) >= 4:
                try:
                    distance_m = float(tokens[3])
                except Exception:
                    distance_m = 0.25
            return self.execute(
                RobotCommand(
                    name="move",
                    params={"direction": direction, "distance_m": distance_m},
                    source=source,
                    timestamp_utc=datetime.now(timezone.utc).isoformat(),
                )
            )

        return "Unknown robotics command. Try: robot status | robot arm | robot follow me | robot move forward 0.5 | robot stop"


_MANAGER: Optional[RoboticsManager] = None


def get_robotics_manager() -> RoboticsManager:
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = RoboticsManager()
    return _MANAGER

