from __future__ import annotations

import json
import os
from typing import Any, Dict


TEMPLATE_APP = """\
from __future__ import annotations

from typing import Any, Dict

from apps.sandbox import safe_open_url, safe_http_get, safe_json


def handle(action: str = "default", params: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    params = dict(params or {})
    context = dict(context or {})
    permissions = list(context.get("permissions", []))
    dry_run = bool(context.get("dry_run", True))

    # Example actions:
    # - recommend: return a short list of entertainment links (dry-run open)
    # - open: open a configured URL (dry-run)
    if action == "recommend":
        links = [
            {"title": "YouTube Subscriptions", "url": "https://www.youtube.com/feed/subscriptions"},
            {"title": "Reddit Frontpage", "url": "https://www.reddit.com/"},
        ]
        return {"recommendations": [safe_open_url(l["url"], permissions, dry_run=dry_run) | {"title": l["title"]} for l in links]}

    return {"message": f"App ran action={action}", "params": params, "context": {"app": context.get("app")}}
"""


def scaffold_app(app_id: str, target_dir: str = "apps/installed") -> str:
    aid = (app_id or "").strip()
    if not aid:
        raise ValueError("app_id is empty")
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in aid)[:64]
    app_dir = os.path.join(target_dir, safe)
    os.makedirs(app_dir, exist_ok=True)

    manifest: Dict[str, Any] = {
        "app_id": safe,
        "name": safe,
        "version": "0.1.0",
        "description": "New third-party app scaffold",
        "entrypoint": "app.py:handle",
        "permissions": ["launch.url"],
    }

    with open(os.path.join(app_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    app_py = os.path.join(app_dir, "app.py")
    if not os.path.exists(app_py):
        with open(app_py, "w") as f:
            f.write(TEMPLATE_APP)

    return app_dir

