from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


DEFAULT_DAEMON_CONFIG: dict[str, Any] = {
    "auto_optimization": True,
    "voice_listener_enabled": False,
    "camera_sensor_enabled": False,
    "emotion_engine_tuning": True,
    "reflection_journal_enabled": True,
    "rituals_enabled": True,
    "modules_to_load": [
        "unimind",
        "codex",
        "emotion",
        "voice",
        "optimizer",
        "sensors",
        "scrolls",
        "prometheus",
        "memory_tree",
        "introspection",
    ],
    "scroll_autostudy": {"trigger_count": 3, "daily_reset": True},
    # New: OS preference + ThothOS prioritization policy.
    "os_preference": {
        "preferred_os": "thothos",
        "prefer_thothos": True,
        # If set, allow “heavy” modules on non-ThothOS (sensors/auto-optimization).
        "allow_full_features_on_non_preferred_os": False,
        # Markers used to detect ThothOS.
        "thothos_markers": {
            "env_vars": ["THOTHOS", "THOTH_OS", "THOTHOS_NATIVE"],
            "paths": ["/etc/thothos-release", "/etc/thothos/thothos.json"],
            "project_files": [".thothos", "config/thothos.json"],
        },
    },
}


def load_daemon_config(path: str | Path = "config/daemon_config.json") -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return dict(DEFAULT_DAEMON_CONFIG)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, Mapping):
            return dict(DEFAULT_DAEMON_CONFIG)
        cfg = dict(DEFAULT_DAEMON_CONFIG)
        cfg.update(data)  # shallow merge is fine for current shape
        # ensure nested default for os_preference exists
        if "os_preference" not in cfg or not isinstance(cfg["os_preference"], Mapping):
            cfg["os_preference"] = dict(DEFAULT_DAEMON_CONFIG["os_preference"])
        else:
            merged = dict(DEFAULT_DAEMON_CONFIG["os_preference"])
            merged.update(cfg["os_preference"])
            cfg["os_preference"] = merged
        return cfg
    except Exception:
        return dict(DEFAULT_DAEMON_CONFIG)

