from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from guardian.ethical_core import EthicalCore
from robotics.types import RobotCommand


@dataclass
class RoboticsSafetyPolicy:
    """
    Keep robotics control safe-by-default.
    - Requires explicit arming for motion/follow
    - Allows stop even when disarmed (failsafe)
    """

    max_move_distance_m: float = 2.0
    require_armed_for_motion: bool = True

    def evaluate(self, command: RobotCommand, *, armed: bool) -> Tuple[bool, Optional[str]]:
        # Ethics gate (basic, but keeps future expansion centralized)
        ethics = EthicalCore()
        verdict = ethics.evaluate_action(command.name)
        if verdict.startswith("Reject:"):
            return False, verdict

        name = command.name.lower().strip()
        if name in {"move", "follow"} and self.require_armed_for_motion and not armed:
            return False, "Robot is not armed. Say 'robot arm' to enable motion."

        if name == "move":
            try:
                distance_m = float(command.params.get("distance_m", 0.25))
            except Exception:
                return False, "Invalid move distance."
            if distance_m < 0:
                return False, "Move distance must be non-negative."
            if distance_m > self.max_move_distance_m:
                return False, f"Move distance too large (max {self.max_move_distance_m}m)."

        return True, None

