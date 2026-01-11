from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from ar_xr.sim.world import Vec3, WorldSpec


@dataclass
class DistilledKnowledge:
    """
    Durable artifact extracted from a simulation run.
    """

    kind: str
    title: str
    summary: str
    heuristics: List[str]
    params: Dict[str, Any]
    keyframes: List[Dict[str, Any]]
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "title": self.title,
            "summary": self.summary,
            "heuristics": self.heuristics,
            "params": self.params,
            "keyframes": self.keyframes,
            "provenance": self.provenance,
        }


def _load_trajectory(path: str, max_points: int = 2000) -> List[Dict[str, Any]]:
    points: List[Dict[str, Any]] = []
    with open(path, "r") as f:
        for line in f:
            if len(points) >= max_points:
                break
            line = line.strip()
            if not line:
                continue
            points.append(json.loads(line))
    return points


def _select_keyframes(points: List[Dict[str, Any]], desired: int = 12) -> List[Dict[str, Any]]:
    if not points:
        return []
    if len(points) <= desired:
        return points
    stride = max(1, len(points) // desired)
    kf = points[::stride]
    if kf[-1] != points[-1]:
        kf.append(points[-1])
    return kf[: desired + 1]


def distill_run(world: WorldSpec, run: Dict[str, Any], trajectory_path: str) -> DistilledKnowledge:
    points = _load_trajectory(trajectory_path)
    keyframes = _select_keyframes(points, desired=12)

    steps = int(run.get("steps", len(points) or 0))
    final_reward = float(run.get("final_reward", 0.0))
    gravity = world.physics.gravity
    dt = float(world.physics.timestep_s)
    drag = float(world.physics.drag)

    heuristics: List[str] = [
        f"Use timestep dt≈{dt:.4f}s; larger dt increases integration error.",
        f"Linear drag≈{drag:.3f} stabilizes motion; too high slows convergence.",
        f"Reward shaping can be distance-to-target (final reward {final_reward:.3f}).",
    ]
    if gravity == (0.0, 0.0, 0.0):
        heuristics.append("Zero-gravity worlds need explicit damping/control to avoid drift.")
    else:
        heuristics.append(f"Gravity={gravity} implies comfort tuning (fall speed, jump impulse) matters.")

    summary = (
        f"Ran {steps} sim steps in '{world.world_id}' and distilled a motion/physics sketch "
        f"into keyframes + control heuristics."
    )
    title = f"XR Sim Distillation: {world.description or world.world_id}"

    return DistilledKnowledge(
        kind=world.kind,
        title=title,
        summary=summary,
        heuristics=heuristics,
        params={
            "physics": {"gravity": gravity, "timestep_s": dt, "drag": drag},
            "steps": steps,
        },
        keyframes=keyframes,
        provenance={"run": run, "trajectory_path": trajectory_path},
    )


def write_knowledge(knowledge: DistilledKnowledge, out_dir: str = "knowledge/ar_xr") -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in "-_." else "_" for c in knowledge.title.lower())[:80]
    json_path = os.path.join(out_dir, f"{safe_title}.json")
    md_path = os.path.join(out_dir, f"{safe_title}.md")

    with open(json_path, "w") as f:
        json.dump(knowledge.to_dict(), f, indent=2)

    md = []
    md.append(f"# {knowledge.title}")
    md.append("")
    md.append(knowledge.summary)
    md.append("")
    md.append("## Heuristics")
    for h in knowledge.heuristics:
        md.append(f"- {h}")
    md.append("")
    md.append("## Params")
    md.append("```json")
    md.append(json.dumps(knowledge.params, indent=2))
    md.append("```")
    md.append("")
    md.append("## Keyframes (trajectory samples)")
    md.append("```json")
    md.append(json.dumps(knowledge.keyframes, indent=2))
    md.append("```")
    md.append("")

    with open(md_path, "w") as f:
        f.write("\n".join(md) + "\n")

    return {"json": json_path, "md": md_path}

