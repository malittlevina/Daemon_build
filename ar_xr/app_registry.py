import json
import os
from typing import Any, Dict, List, Optional


DEFAULT_APPS: List[Dict[str, Any]] = [
    {
        "id": "webxr-sample",
        "name": "WebXR Sample",
        "kind": "xr",
        "runtime": "webxr",
        "launch": {"type": "url", "value": "https://immersiveweb.dev/"},
        "notes": "Opens a WebXR-capable page in a browser (if available).",
        "tags": ["demo", "web"],
    },
    {
        "id": "openxr-tooling",
        "name": "OpenXR Tooling Check",
        "kind": "xr",
        "runtime": "openxr",
        "launch": {"type": "command", "value": "openxr-info"},
        "notes": "Runs OpenXR runtime info tool (if installed).",
        "tags": ["diagnostics"],
    },
]


class ARXRAppRegistry:
    """
    Simple persistent registry for AR/XR launch targets.

    Stored as JSON so agents can modify it easily.
    """

    def __init__(self, registry_path: str = "config/ar_xr_apps.json"):
        self.registry_path = registry_path
        self._apps: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r") as f:
                    data = json.load(f)
                self._apps = data.get("apps", []) if isinstance(data, dict) else list(data)
                return
            except Exception:
                # Fall back to defaults if corrupted.
                self._apps = list(DEFAULT_APPS)
                return

        self._apps = list(DEFAULT_APPS)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump({"apps": self._apps}, f, indent=2)

    def list_apps(self, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        if not kind:
            return list(self._apps)
        kind_l = kind.lower()
        return [a for a in self._apps if str(a.get("kind", "")).lower() == kind_l]

    def get_by_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        app_id_l = (app_id or "").strip().lower()
        for app in self._apps:
            if str(app.get("id", "")).lower() == app_id_l:
                return app
        return None

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        name_l = (name or "").strip().lower()
        if not name_l:
            return None
        for app in self._apps:
            if str(app.get("name", "")).strip().lower() == name_l:
                return app
        # soft match
        for app in self._apps:
            if name_l in str(app.get("name", "")).strip().lower():
                return app
        return None

    def register_app(self, app: Dict[str, Any], persist: bool = True) -> Dict[str, Any]:
        if "id" not in app:
            raise ValueError("App must include an 'id'")
        existing = self.get_by_id(app["id"])
        if existing:
            existing.update(app)
        else:
            self._apps.append(app)
        if persist:
            self.save()
        return app

