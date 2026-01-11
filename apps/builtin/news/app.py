from __future__ import annotations

from typing import Any, Dict

from apps.sandbox import safe_open_url


def handle(action: str = "default", params: Dict[str, Any] | None = None, context: Dict[str, Any] | None = None):
    params = dict(params or {})
    context = dict(context or {})
    permissions = list(context.get("permissions", []))
    dry_run = bool(context.get("dry_run", True))

    if action in {"default", "topics"}:
        topics = ["technology", "science", "business", "world", "gaming", "xr", "ai"]
        return {"topics": topics}

    if action == "open":
        topic = str(params.get("topic", "technology")).strip().lower() or "technology"
        url = f"https://news.google.com/search?q={topic}"
        return {"topic": topic, "open": safe_open_url(url, permissions, dry_run=dry_run)}

    if action == "headlines":
        # Uses existing thirdparty/news.py (requires YOUR_NEWSAPI_KEY configured there or replaced)
        topic = str(params.get("topic", "technology")).strip().lower() or "technology"
        try:
            from thirdparty.news import fetch_latest_news

            return {"topic": topic, "headlines": fetch_latest_news(topic=topic)}
        except Exception as e:
            return {"topic": topic, "error": str(e), "hint": "Configure NewsAPI key or use action=open."}

    return {"message": f"Unknown action: {action}", "hint": "Try: topics | open | headlines"}

