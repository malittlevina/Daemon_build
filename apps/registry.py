from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AppManifest:
    app_id: str
    name: str
    version: str
    description: str = ""
    entrypoint: str = "app.py:handle"
    permissions: List[str] = None  # type: ignore[assignment]
    source: str = "builtin"  # builtin | installed
    path: str = ""

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "entrypoint": self.entrypoint,
            "permissions": list(self.permissions or []),
            "source": self.source,
        }


class AppRegistry:
    def __init__(self, builtin_dir: str = "apps/builtin", installed_dir: str = "apps/installed"):
        self.builtin_dir = builtin_dir
        self.installed_dir = installed_dir

    def _load_manifest(self, manifest_path: str, source: str) -> Optional[AppManifest]:
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            app_id = str(data["app_id"])
            return AppManifest(
                app_id=app_id,
                name=str(data.get("name", app_id)),
                version=str(data.get("version", "0.0.0")),
                description=str(data.get("description", "")),
                entrypoint=str(data.get("entrypoint", "app.py:handle")),
                permissions=list(data.get("permissions", []) or []),
                source=source,
                path=os.path.dirname(manifest_path),
            )
        except Exception:
            return None

    def _discover_dir(self, base_dir: str, source: str) -> List[AppManifest]:
        if not os.path.isdir(base_dir):
            return []
        out: List[AppManifest] = []
        for name in os.listdir(base_dir):
            app_dir = os.path.join(base_dir, name)
            if not os.path.isdir(app_dir):
                continue
            manifest_path = os.path.join(app_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                continue
            m = self._load_manifest(manifest_path, source=source)
            if m:
                out.append(m)
        return out

    def list_apps(self) -> List[Dict[str, Any]]:
        apps = self._discover_dir(self.builtin_dir, "builtin") + self._discover_dir(self.installed_dir, "installed")
        apps.sort(key=lambda a: (a.source, a.app_id))
        return [a.to_public_dict() for a in apps]

    def get_manifest(self, app_id: str) -> Optional[AppManifest]:
        app_id_l = (app_id or "").strip().lower()
        for m in self._discover_dir(self.builtin_dir, "builtin") + self._discover_dir(self.installed_dir, "installed"):
            if m.app_id.lower() == app_id_l:
                return m
        return None

