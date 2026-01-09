from __future__ import annotations

from typing import Any, Dict


CURRENT_SCHEMA_VERSION = 2


def migrate_state_dict(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate a serialized RealmState dict to CURRENT_SCHEMA_VERSION.

    Keep migrations:
    - deterministic
    - additive (prefer adding new fields with defaults)
    - backwards compatible for old snapshots/logs
    """

    v = int(state.get("schema_version") or 1)
    out: Dict[str, Any] = dict(state)

    if v < 2:
        # v2 introduces `goals` as a first-class world substrate.
        out.setdefault("goals", {})
        out["schema_version"] = 2
        v = 2

    # Future migrations go here.
    out["schema_version"] = int(out.get("schema_version") or CURRENT_SCHEMA_VERSION)
    return out

