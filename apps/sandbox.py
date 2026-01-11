from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, Optional


class PermissionError(Exception):
    pass


def require_permission(permissions: list[str], needed: str) -> None:
    if needed not in (permissions or []):
        raise PermissionError(f"Missing permission: {needed}")


def safe_http_get(url: str, permissions: list[str], timeout_s: int = 10) -> str:
    require_permission(permissions, "network")
    with urllib.request.urlopen(url, timeout=timeout_s) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def safe_open_url(url: str, permissions: list[str], dry_run: bool = True) -> Dict[str, Any]:
    require_permission(permissions, "launch.url")
    if dry_run:
        return {"ok": True, "dry_run": True, "url": url}
    # Deliberately not executing xdg-open here; keep launch behavior centralized in XR subsystem / dedicated launcher.
    return {"ok": False, "error": "Non-dry-run URL launch is disabled by policy."}


def safe_json(data: Any) -> str:
    return json.dumps(data, default=str)

