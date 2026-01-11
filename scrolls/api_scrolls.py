from __future__ import annotations

from typing import Any, Dict, Optional

def fetch_weather(city):
    try:
        import requests
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
        return response.text
    except Exception as e:
        return f"Weather fetch failed: {e}"

def get_news_headlines(api_key, topic="technology"):
    try:
        import requests
        url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={api_key}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            headlines = [article['title'] for article in res.json().get('articles', [])]
            return headlines
        else:
            return [f"Failed to fetch news: {res.status_code}"]
    except Exception as e:
        return [f"News fetch failed: {e}"]

def scroll_invoke_weather(city):
    print(f"[SCROLL] Weather Ritual: {fetch_weather(city)}")

def execute_api_scroll(name: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs):
    """
    Execute an API-based scroll.

    Supports flexible calling conventions so ScrollEngine can pass either:
    - execute_api_scroll(name, context)
    - execute_api_scroll(name=name, context=context)
    """
    ctx = dict(context or {})
    ctx.update(kwargs)

    if not name:
        return "[api_scrolls] No scroll name provided."

    name_l = str(name).lower().strip()
    if name_l == "fetch weather":
        city = ctx.get("city", "Denver")
        msg = fetch_weather(city)
        print(f"[SCROLL] Weather Ritual: {msg}")
        return msg

    if name_l == "get news":
        headlines = get_news_headlines(ctx.get("api_key", ""), ctx.get("topic", "technology"))
        for headline in headlines:
            print(f"[SCROLL] News Headline: {headline}")
        return headlines

    return f"[api_scrolls] Unknown API scroll: {name}"
