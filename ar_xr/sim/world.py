from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


Vec3 = Tuple[float, float, float]


@dataclass
class PhysicsSpec:
    gravity: Vec3 = (0.0, -9.81, 0.0)
    timestep_s: float = 1.0 / 60.0
    drag: float = 0.02  # simple linear drag


@dataclass
class EntitySpec:
    entity_id: str
    kind: str = "dynamic"  # dynamic | static | kinematic
    shape: str = "sphere"  # sphere | box (symbolic)
    mass: float = 1.0
    position: Vec3 = (0.0, 0.0, 0.0)
    velocity: Vec3 = (0.0, 0.0, 0.0)
    tags: List[str] = field(default_factory=list)
    props: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSpec:
    agent_id: str = "daemon"
    body_entity_id: str = "agent_body"
    spawn_position: Vec3 = (0.0, 1.6, 0.0)
    action_space: List[str] = field(
        default_factory=lambda: ["thrust_x", "thrust_y", "thrust_z", "jump", "grab"]
    )


@dataclass
class WorldSpec:
    world_id: str
    kind: str = "xr"
    description: str = ""
    physics: PhysicsSpec = field(default_factory=PhysicsSpec)
    entities: List[EntitySpec] = field(default_factory=list)
    agent: AgentSpec = field(default_factory=AgentSpec)
    goals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "kind": self.kind,
            "description": self.description,
            "physics": {
                "gravity": self.physics.gravity,
                "timestep_s": self.physics.timestep_s,
                "drag": self.physics.drag,
            },
            "entities": [
                {
                    "entity_id": e.entity_id,
                    "kind": e.kind,
                    "shape": e.shape,
                    "mass": e.mass,
                    "position": e.position,
                    "velocity": e.velocity,
                    "tags": e.tags,
                    "props": e.props,
                }
                for e in self.entities
            ],
            "agent": {
                "agent_id": self.agent.agent_id,
                "body_entity_id": self.agent.body_entity_id,
                "spawn_position": self.agent.spawn_position,
                "action_space": self.agent.action_space,
            },
            "goals": self.goals,
            "metadata": self.metadata,
        }


def synthesize_world(goal: str, kind: str = "xr", world_id: Optional[str] = None) -> WorldSpec:
    """
    Agent-native world synthesis: turn a goal into a symbolic world spec.

    This is intentionally engine-agnostic; an adapter can map it to Godot/Unity/OpenXR/etc.
    """
    g = (goal or "").strip()
    wid = world_id or "world_xr_training"
    kind_l = (kind or "xr").lower().strip()

    entities: List[EntitySpec] = [
        EntitySpec(entity_id="floor", kind="static", shape="box", mass=0.0, position=(0.0, 0.0, 0.0), tags=["ground"]),
        EntitySpec(entity_id="target", kind="static", shape="sphere", mass=0.0, position=(2.0, 1.0, 0.0), tags=["goal"]),
        EntitySpec(entity_id="obstacle", kind="static", shape="box", mass=0.0, position=(1.0, 0.5, 0.0), tags=["hazard"]),
        EntitySpec(entity_id="agent_body", kind="dynamic", shape="sphere", mass=70.0, position=(0.0, 1.6, 0.0), tags=["agent"]),
    ]

    physics = PhysicsSpec()
    if "zero g" in g.lower() or "zero-g" in g.lower():
        physics.gravity = (0.0, 0.0, 0.0)
    if "slow" in g.lower():
        physics.timestep_s = 1.0 / 30.0

    return WorldSpec(
        world_id=wid,
        kind=kind_l,
        description=g or "XR training world",
        physics=physics,
        entities=entities,
        agent=AgentSpec(spawn_position=(0.0, 1.6, 0.0)),
        goals=[g] if g else ["reach target"],
        metadata={"synthesized": True},
    )

