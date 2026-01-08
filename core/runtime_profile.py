from __future__ import annotations

import importlib.util
import os
import platform
from dataclasses import dataclass, field
from typing import Any


def _is_truthy_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "off", "null", "none"}


@dataclass(frozen=True)
class HostOSInfo:
    system: str
    release: str
    version: str
    machine: str
    python_version: str


@dataclass(frozen=True)
class SymbolicOSInfo:
    """
    "Symbolic OS" means: the host environment is our intended OS/runtime.
    Detection is intentionally heuristic + configurable so the daemon stays portable.
    """

    os_id: str
    is_native: bool
    confidence: float
    markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityInfo:
    has_voice: bool
    has_vision: bool
    has_ruff: bool
    has_ollama: bool


@dataclass(frozen=True)
class RuntimeProfile:
    host: HostOSInfo
    symbolic_os: SymbolicOSInfo
    capabilities: CapabilityInfo
    mode: str  # "native" | "portable"
    preference_score: float
    meta: dict[str, Any] = field(default_factory=dict)


def detect_host_os() -> HostOSInfo:
    return HostOSInfo(
        system=platform.system(),
        release=platform.release(),
        version=platform.version(),
        machine=platform.machine(),
        python_version=platform.python_version(),
    )


def detect_capabilities() -> CapabilityInfo:
    def has(module: str) -> bool:
        return importlib.util.find_spec(module) is not None

    # Keep these as best-effort. Missing deps should just disable the subsystem.
    return CapabilityInfo(
        has_voice=has("speech_recognition"),
        has_vision=has("cv2"),
        has_ruff=has("ruff"),
        has_ollama=has("ollama"),
    )


def detect_symbolic_os(policy: dict[str, Any] | None = None) -> SymbolicOSInfo:
    policy = policy or {}
    os_id = str(policy.get("preferred_os_id") or "prometheus_os")

    env_markers: list[str] = list((policy.get("native_markers") or {}).get("env") or [])
    file_markers: list[str] = list((policy.get("native_markers") or {}).get("files") or [])

    markers: list[str] = []
    confidence = 0.0

    for env_key in env_markers:
        if _is_truthy_env(os.environ.get(env_key)):
            markers.append(f"env:{env_key}")
            confidence += 0.6

    # Allow both absolute and relative markers; relative resolves from CWD.
    cwd = os.getcwd()
    for path in file_markers:
        resolved = path if os.path.isabs(path) else os.path.join(cwd, path)
        if os.path.exists(resolved):
            markers.append(f"file:{path}")
            confidence += 0.3

    is_native = confidence >= 0.6
    confidence = min(confidence, 1.0)

    return SymbolicOSInfo(
        os_id=os_id,
        is_native=is_native,
        confidence=confidence,
        markers=tuple(markers),
    )


def build_runtime_profile(os_policy: dict[str, Any] | None = None) -> RuntimeProfile:
    host = detect_host_os()
    capabilities = detect_capabilities()
    symbolic = detect_symbolic_os(os_policy or {})

    mode = "native" if symbolic.is_native else "portable"
    preference_score = 1.0 if symbolic.is_native else 0.25

    return RuntimeProfile(
        host=host,
        symbolic_os=symbolic,
        capabilities=capabilities,
        mode=mode,
        preference_score=preference_score,
        meta={},
    )
