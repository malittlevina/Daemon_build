from __future__ import annotations

from typing import Any, Dict

from apps.sandbox import safe_open_url


DEFAULT_SOCIAL_LINKS = {
    "x": "https://x.com/",
    "twitter": "https://x.com/",
    "instagram": "https://www.instagram.com/",
    "tiktok": "https://www.tiktok.com/",
    "reddit": "https://www.reddit.com/",
    "discord": "https://discord.com/app",
}


def handle(action: str = "default", params: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    params = dict(params or {})
    context = dict(context or {})
    permissions = list(context.get("permissions", []))
    dry_run = bool(context.get("dry_run", True))

    if action in {"default", "list"}:
        return {"platforms": sorted(DEFAULT_SOCIAL_LINKS.keys()), "note": "Use action=open with platform param."}

    if action == "open":
        platform = str(params.get("platform", "")).strip().lower()
        if not platform:
            return {"ok": False, "error": "Missing param: platform"}
        url = DEFAULT_SOCIAL_LINKS.get(platform)
        if not url:
            return {"ok": False, "error": f"Unknown platform: {platform}", "platforms": sorted(DEFAULT_SOCIAL_LINKS.keys())}
        return {"ok": True, "platform": platform, "open": safe_open_url(url, permissions, dry_run=dry_run)}

    return {"message": f"Unknown action: {action}", "hint": "Try: list | open (with platform)"}

