import json
import os
import time
from typing import Any, Dict, List, Optional


DEFAULT_TRAINING_MODULES: List[Dict[str, Any]] = [
    {
        "id": "xr-safety-basics",
        "kind": "xr",
        "title": "XR Safety Basics",
        "objectives": [
            "Identify common XR safety risks (motion sickness, boundaries, cable hazards)",
            "Configure guardian/boundary and comfort settings",
        ],
        "drills": [
            "Set a boundary and verify it triggers at edge",
            "Run a 5-minute comfort test and record symptoms",
        ],
    },
    {
        "id": "xr-interaction-fundamentals",
        "kind": "xr",
        "title": "XR Interaction Fundamentals",
        "objectives": [
            "Practice grab/throw/teleport interactions",
            "Understand input mapping and affordances",
        ],
        "drills": [
            "Do 20 grab/place reps with alternating hands",
            "Teleport between 5 points and minimize overshoot",
        ],
    },
    {
        "id": "ar-spatial-anchors",
        "kind": "ar",
        "title": "AR Spatial Anchors & Tracking",
        "objectives": [
            "Understand plane detection, anchors, and drift",
            "Create stable anchor placement heuristics",
        ],
        "drills": [
            "Place 3 anchors on distinct planes and verify persistence",
            "Record drift after walking a 10m loop",
        ],
    },
]


def load_training_modules(path: str = "config/ar_xr_training_modules.json") -> List[Dict[str, Any]]:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            modules = data.get("modules", []) if isinstance(data, dict) else list(data)
            return modules if modules else list(DEFAULT_TRAINING_MODULES)
        except Exception:
            return list(DEFAULT_TRAINING_MODULES)
    return list(DEFAULT_TRAINING_MODULES)


def save_training_modules(modules: List[Dict[str, Any]], path: str = "config/ar_xr_training_modules.json") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"modules": modules}, f, indent=2)


def build_training_plan(goal: str, kind: str, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Agent-native heuristic planner: selects 1-3 modules matching kind and goal keywords.
    """
    goal_l = (goal or "").lower()
    kind_l = (kind or "").lower().strip() or "xr"

    candidates = [m for m in modules if str(m.get("kind", "")).lower() == kind_l]
    if not candidates:
        candidates = list(modules)

    scored: List[tuple[int, Dict[str, Any]]] = []
    for m in candidates:
        score = 0
        blob = " ".join(
            [
                str(m.get("id", "")),
                str(m.get("title", "")),
                " ".join(m.get("objectives", []) or []),
                " ".join(m.get("drills", []) or []),
            ]
        ).lower()
        for token in [t for t in goal_l.split() if len(t) > 2]:
            if token in blob:
                score += 1
        scored.append((score, m))

    scored.sort(key=lambda x: (x[0], str(x[1].get("title", ""))), reverse=True)
    selected = [m for score, m in scored[:3] if score > 0] or [scored[0][1]] if scored else []

    return {
        "kind": kind_l,
        "goal": goal,
        "modules": [
            {
                "id": m.get("id"),
                "title": m.get("title"),
                "objectives": m.get("objectives", []),
                "drills": m.get("drills", []),
            }
            for m in selected
        ],
    }


def start_training_session(
    plan: Dict[str, Any],
    session_id: Optional[str] = None,
    log_path: str = "logs/ar_xr_training.log",
) -> Dict[str, Any]:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    sid = session_id or f"arxr-{int(time.time())}"

    session = {
        "session_id": sid,
        "started_at": time.time(),
        "plan": plan,
        "status": "started",
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(session) + "\n")

    return session

