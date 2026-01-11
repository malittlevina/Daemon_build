from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from ar_xr.sim.world import Vec3, WorldSpec


PolicyFn = Callable[[int, Vec3, Vec3], Dict[str, Any]]


def make_hover_thrust_policy(world: WorldSpec, gain: float) -> PolicyFn:
    """
    Returns a simple controller:
    - directional thrust toward target scaled by gain
    - optional hover compensation to counter gravity

    This isn't "RL" yet, but it produces a tunable policy that can be searched over episodes.
    """
    entity_map = {e.entity_id: e for e in world.entities}
    agent_ent = entity_map.get(world.agent.body_entity_id)
    mass = float(agent_ent.mass) if agent_ent and agent_ent.mass else 70.0
    g = world.physics.gravity

    # Force needed to counter gravity: F = -g * m
    hover = (0.0, -g[1] * mass, 0.0)

    def policy(step_idx: int, agent_pos: Vec3, target_pos: Vec3) -> Dict[str, Any]:
        dx = (target_pos[0] - agent_pos[0], target_pos[1] - agent_pos[1], target_pos[2] - agent_pos[2])
        mag = (dx[0] * dx[0] + dx[1] * dx[1] + dx[2] * dx[2]) ** 0.5 or 1.0
        unit = (dx[0] / mag, dx[1] / mag, dx[2] / mag)
        toward = (unit[0] * gain, unit[1] * gain, unit[2] * gain)
        thrust = (toward[0] + hover[0], toward[1] + hover[1], toward[2] + hover[2])
        return {"thrust": thrust, "policy": {"type": "hover_thrust", "gain": gain}}

    return policy


@dataclass
class EpisodeResult:
    gain: float
    final_reward: float
    run: Dict[str, Any]
    trajectory_path: str


class ThrustGainSearchLearner:
    """
    Simple episode search across gains. Keeps the best run.
    """

    def __init__(self, gains: Optional[List[float]] = None):
        self.gains = gains or [5.0, 25.0, 100.0, 250.0]

    def run(self, world: WorldSpec, run_episode) -> Tuple[EpisodeResult, List[EpisodeResult]]:
        all_results: List[EpisodeResult] = []
        best: Optional[EpisodeResult] = None

        for gain in self.gains:
            policy = make_hover_thrust_policy(world, gain=gain)
            sim = run_episode(policy)
            run = sim["run"]
            ep = EpisodeResult(
                gain=gain,
                final_reward=float(run.get("final_reward", 0.0)),
                run=run,
                trajectory_path=sim["trajectory_path"],
            )
            all_results.append(ep)
            if best is None or ep.final_reward > best.final_reward:
                best = ep

        # best is guaranteed because gains is non-empty
        return best or all_results[0], all_results

