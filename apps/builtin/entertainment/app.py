from __future__ import annotations

from typing import Any, Dict

from apps.sandbox import safe_open_url


def handle(action: str = "default", params: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    params = dict(params or {})
    context = dict(context or {})
    permissions = list(context.get("permissions", []))
    dry_run = bool(context.get("dry_run", True))

    if action in {"default", "recommend"}:
        links = [
            {"title": "YouTube Subscriptions", "url": "https://www.youtube.com/feed/subscriptions"},
            {"title": "Netflix", "url": "https://www.netflix.com/"},
            {"title": "Twitch Following", "url": "https://www.twitch.tv/directory/following"},
            {"title": "Reddit Frontpage", "url": "https://www.reddit.com/"},
        ]
        recs = []
        for l in links:
            rec = safe_open_url(l["url"], permissions, dry_run=dry_run)
            rec["title"] = l["title"]
            recs.append(rec)
        return {"recommendations": recs, "note": "Links are dry-run by default."}

    return {"message": f"Unknown action: {action}", "hint": "Try: recommend"}

