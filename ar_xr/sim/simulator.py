from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ar_xr.sim.world import Vec3, WorldSpec


def _v_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _v_mul(a: Vec3, s: float) -> Vec3:
    return (a[0] * s, a[1] * s, a[2] * s)


def _v_len(a: Vec3) -> float:
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _v_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


@dataclass
class SimStep:
    t: float
    agent_pos: Vec3
    agent_vel: Vec3
    reward: float


def _default_policy(step_idx: int, agent_pos: Vec3, target_pos: Vec3) -> Dict[str, Any]:
    """
    Very simple policy: thrust toward target with capped magnitude.
    """
    dx = _v_sub(target_pos, agent_pos)
    mag = _v_len(dx) or 1.0
    unit = (dx[0] / mag, dx[1] / mag, dx[2] / mag)
    thrust = _v_mul(unit, 3.0)
    return {"thrust": thrust}


def run_headless_episode(
    world: WorldSpec,
    steps: int = 300,
    run_dir: Optional[str] = None,
    policy=None,
) -> Dict[str, Any]:
    """
    Minimal headless simulator:
    - Integrates a single dynamic agent body under gravity + drag
    - Applies policy thrust each step
    - Logs trajectory to run_dir/trajectory.jsonl
    """
    run_id = f"sim-{int(time.time())}"
    out_dir = run_dir or os.path.join("sandbox", "ar_xr_runs", run_id)
    os.makedirs(out_dir, exist_ok=True)

    entity_map = {e.entity_id: e for e in world.entities}
    agent_ent = entity_map.get(world.agent.body_entity_id)
    target_ent = entity_map.get("target")

    if not agent_ent:
        raise ValueError("World is missing agent body entity")
    if not target_ent:
        raise ValueError("World is missing 'target' entity")

    dt = float(world.physics.timestep_s)
    g = world.physics.gravity
    drag = float(world.physics.drag)

    pos = agent_ent.position
    vel = agent_ent.velocity
    target_pos = target_ent.position

    traj_path = os.path.join(out_dir, "trajectory.jsonl")
    steps_out: List[SimStep] = []

    for i in range(int(steps)):
        pol = policy(i, pos, target_pos) if callable(policy) else _default_policy(i, pos, target_pos)
        thrust = pol.get("thrust", (0.0, 0.0, 0.0))

        # Acceleration = gravity + thrust/mass - drag*vel
        inv_m = 0.0 if agent_ent.mass <= 0 else 1.0 / float(agent_ent.mass)
        acc = _v_add(g, _v_add(_v_mul(thrust, inv_m), _v_mul(vel, -drag)))

        vel = _v_add(vel, _v_mul(acc, dt))
        pos = _v_add(pos, _v_mul(vel, dt))

        dist = _v_len(_v_sub(target_pos, pos))
        reward = -dist
        step = SimStep(t=i * dt, agent_pos=pos, agent_vel=vel, reward=reward)
        steps_out.append(step)

        with open(traj_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "t": step.t,
                        "agent_pos": step.agent_pos,
                        "agent_vel": step.agent_vel,
                        "reward": step.reward,
                    }
                )
                + "\n"
            )

        # early stop near target
        if dist < 0.15:
            break

    summary = {
        "run_id": run_id,
        "run_dir": out_dir,
        "steps": len(steps_out),
        "final_pos": pos,
        "final_vel": vel,
        "final_reward": steps_out[-1].reward if steps_out else 0.0,
    }
    with open(os.path.join(out_dir, "run_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return {"run": summary, "trajectory_path": traj_path}

