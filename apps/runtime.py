from __future__ import annotations

import importlib.util
import os
from typing import Any, Callable, Dict, Optional, Tuple

from apps.registry import AppManifest, AppRegistry


def _load_callable_from_path(module_path: str, func_name: str) -> Callable[..., Any]:
    spec = importlib.util.spec_from_file_location(f"apps_user_{os.path.basename(module_path)}", module_path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module: {module_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    fn = getattr(mod, func_name, None)
    if not callable(fn):
        raise AttributeError(f"Entrypoint function not found: {func_name}")
    return fn


def _resolve_entrypoint(manifest: AppManifest) -> Tuple[str, str]:
    ep = manifest.entrypoint or "app.py:handle"
    if ":" not in ep:
        return ep, "handle"
    file_part, fn_part = ep.split(":", 1)
    return file_part.strip(), fn_part.strip() or "handle"


class AppRuntime:
    def __init__(self, registry: Optional[AppRegistry] = None):
        self.registry = registry or AppRegistry()

    def describe(self, app_id: str) -> Dict[str, Any]:
        m = self.registry.get_manifest(app_id)
        if not m:
            return {"ok": False, "error": f"Unknown app: {app_id}"}
        return {"ok": True, "app": m.to_public_dict()}

    def run(
        self,
        app_id: str,
        action: str = "default",
        params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        m = self.registry.get_manifest(app_id)
        if not m:
            return {"ok": False, "error": f"Unknown app: {app_id}"}

        file_part, fn_part = _resolve_entrypoint(m)
        module_path = os.path.join(m.path, file_part)
        fn = _load_callable_from_path(module_path, fn_part)

        ctx = dict(context or {})
        ctx["app"] = m.to_public_dict()
        ctx["permissions"] = list(m.permissions or [])
        ctx["dry_run"] = bool(dry_run)

        try:
            result = fn(action=action, params=dict(params or {}), context=ctx)
            return {"ok": True, "app_id": m.app_id, "action": action, "result": result}
        except Exception as e:
            return {"ok": False, "app_id": m.app_id, "error": str(e)}

