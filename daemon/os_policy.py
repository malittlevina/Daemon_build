from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

from core.runtime_profile import RuntimeProfile, build_runtime_profile


def load_daemon_config(path: str = "config/daemon_config.json") -> dict[str, Any]:
    """
    Best-effort config loader. Missing/invalid config should never prevent daemon boot.
    """
    try:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def apply_os_policy(config: dict[str, Any], profile: RuntimeProfile) -> dict[str, Any]:
    """
    Host-OS compatible defaults + "prefer our OS" behavior.

    Rules:
    - Always boot on any host OS.
    - If running on our symbolic OS (native mode), allow full feature set (still gated by deps).
    - If portable, default-disable OS-coupled subsystems unless explicitly forced.
    """
    cfg: dict[str, Any] = deepcopy(config or {})
    os_policy: dict[str, Any] = dict(cfg.get("os_policy") or {})

    prefer_native = bool(os_policy.get("prefer_native", True))
    force_portable_sensors = bool(os_policy.get("force_portable_sensors", False))
    force_portable_voice = bool(os_policy.get("force_portable_voice", False))
    force_portable_auto_optimization = bool(os_policy.get("force_portable_auto_optimization", False))

    effective_mode = profile.mode
    cfg["runtime_mode"] = effective_mode
    cfg["preferred_os_id"] = profile.symbolic_os.os_id
    cfg["symbolic_os_detected"] = {
        "is_native": profile.symbolic_os.is_native,
        "confidence": profile.symbolic_os.confidence,
        "markers": list(profile.symbolic_os.markers),
    }

    # If the user doesn't want "prefer native", we still keep portable safety checks.
    is_native = profile.symbolic_os.is_native and prefer_native

    # Voice
    if not profile.capabilities.has_voice:
        cfg["voice_listener_enabled"] = False
        cfg.setdefault("runtime_warnings", []).append(
            "voice_listener disabled: missing dependency 'speech_recognition'"
        )
    elif not is_native and not force_portable_voice:
        cfg["voice_listener_enabled"] = False
        cfg.setdefault("runtime_warnings", []).append(
            "voice_listener disabled in portable mode (set os_policy.force_portable_voice=true to override)"
        )

    # Camera / vision
    if not profile.capabilities.has_vision:
        cfg["camera_sensor_enabled"] = False
        cfg.setdefault("runtime_warnings", []).append("camera_sensor disabled: missing dependency 'cv2'")
    elif not is_native and not force_portable_sensors:
        cfg["camera_sensor_enabled"] = False
        cfg.setdefault("runtime_warnings", []).append(
            "camera_sensor disabled in portable mode (set os_policy.force_portable_sensors=true to override)"
        )

    # Auto optimization (calls ruff)
    if not profile.capabilities.has_ruff:
        cfg["auto_optimization"] = False
        cfg.setdefault("runtime_warnings", []).append("auto_optimization disabled: 'ruff' not available")
    elif not is_native and not force_portable_auto_optimization:
        cfg["auto_optimization"] = False
        cfg.setdefault("runtime_warnings", []).append(
            "auto_optimization disabled in portable mode (set os_policy.force_portable_auto_optimization=true to override)"
        )

    return cfg


def build_configured_profile_and_config(
    config_path: str = "config/daemon_config.json",
) -> tuple[RuntimeProfile, dict[str, Any]]:
    cfg = load_daemon_config(config_path)
    profile = build_runtime_profile(os_policy=dict(cfg.get("os_policy") or {}))
    cfg = apply_os_policy(cfg, profile)
    return profile, cfg
