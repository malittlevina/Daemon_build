from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import platform
from typing import Any, Mapping


@dataclass(frozen=True)
class RuntimeContext:
    """
    Host/runtime context for daemon boot decisions.

    Design intent:
    - Run on any OS (Linux/macOS/Windows) in compatibility mode.
    - Prefer/enable richer integrations when we detect ThothOS.
    """

    host_os: str
    host_os_version: str | None
    host_arch: str | None

    is_thothos: bool
    thothos_detection_reason: str

    compatibility_mode: bool
    preference_policy: str

    markers: dict[str, str] = field(default_factory=dict)


DEFAULT_THOTHOS_MARKERS: dict[str, Any] = {
    # If any of these env vars are present (any value), we treat it as ThothOS.
    "env_vars": ["THOTHOS", "THOTH_OS", "THOTHOS_NATIVE"],
    # If any of these paths exist, we treat it as ThothOS.
    "paths": ["/etc/thothos-release", "/etc/thothos/thothos.json"],
    # If any of these files exist in the project root, we treat it as ThothOS.
    "project_files": [".thothos", "config/thothos.json"],
}


def _first_existing_path(paths: list[str]) -> str | None:
    for p in paths:
        try:
            if Path(p).exists():
                return p
        except Exception:
            # Some OSes/filesystems may throw for special paths; ignore safely.
            continue
    return None


def _first_present_env(env_vars: list[str]) -> str | None:
    for key in env_vars:
        if os.getenv(key) is not None:
            return key
    return None


def detect_runtime_context(
    *,
    project_root: str | Path | None = None,
    config: Mapping[str, Any] | None = None,
) -> RuntimeContext:
    system = platform.system() or "Unknown"
    host_os = system.lower()
    host_os_version = platform.version() or None
    host_arch = platform.machine() or None

    root = Path(project_root) if project_root is not None else Path.cwd()

    os_pref = (config or {}).get("os_preference") if isinstance(config, Mapping) else None
    os_pref = os_pref if isinstance(os_pref, Mapping) else {}

    markers_cfg = os_pref.get("thothos_markers")
    markers_cfg = markers_cfg if isinstance(markers_cfg, Mapping) else {}

    env_vars = markers_cfg.get("env_vars") or DEFAULT_THOTHOS_MARKERS["env_vars"]
    paths = markers_cfg.get("paths") or DEFAULT_THOTHOS_MARKERS["paths"]
    project_files = markers_cfg.get("project_files") or DEFAULT_THOTHOS_MARKERS["project_files"]

    # Normalize types defensively
    env_vars = [str(x) for x in env_vars] if isinstance(env_vars, list) else DEFAULT_THOTHOS_MARKERS["env_vars"]
    paths = [str(x) for x in paths] if isinstance(paths, list) else DEFAULT_THOTHOS_MARKERS["paths"]
    project_files = (
        [str(x) for x in project_files] if isinstance(project_files, list) else DEFAULT_THOTHOS_MARKERS["project_files"]
    )

    detected_env = _first_present_env(env_vars)
    detected_path = _first_existing_path(paths)
    detected_project_file: str | None = None
    for rel in project_files:
        try:
            candidate = (root / rel).resolve()
            if candidate.exists():
                detected_project_file = str(candidate)
                break
        except Exception:
            continue

    is_thothos = any([detected_env, detected_path, detected_project_file])
    if detected_env:
        reason = f"env:{detected_env}"
    elif detected_path:
        reason = f"path:{detected_path}"
    elif detected_project_file:
        reason = f"project_file:{detected_project_file}"
    else:
        reason = "no_thothos_markers_found"

    prefer_thothos = os_pref.get("prefer_thothos", True)
    compatibility_mode = bool(prefer_thothos and not is_thothos)
    policy = "prefer_thothos" if prefer_thothos else "no_preference"

    markers: dict[str, str] = {}
    if detected_env:
        markers["thothos_env"] = detected_env
    if detected_path:
        markers["thothos_path"] = detected_path
    if detected_project_file:
        markers["thothos_project_file"] = detected_project_file

    return RuntimeContext(
        host_os=host_os,
        host_os_version=host_os_version,
        host_arch=host_arch,
        is_thothos=is_thothos,
        thothos_detection_reason=reason,
        compatibility_mode=compatibility_mode,
        preference_policy=policy,
        markers=markers,
    )

