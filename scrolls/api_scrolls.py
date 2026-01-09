# scrolls/api_scrolls.py
import requests

def fetch_weather(city):
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        return response.text
    except requests.RequestException as e:
        return f"Weather fetch failed: {e}"

def get_news_headlines(api_key, topic="technology"):
    try:
        url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={api_key}"
        res = requests.get(url)
        if res.status_code == 200:
            headlines = [article['title'] for article in res.json().get('articles', [])]
            return headlines
        else:
            return [f"Failed to fetch news: {res.status_code}"]
    except requests.RequestException as e:
        return [f"News fetch failed: {e}"]

def scroll_invoke_weather(city):
    print(f"[SCROLL] Weather Ritual: {fetch_weather(city)}")

def execute_api_scroll(name, context):
    if name == "fetch weather":
        city = context.get("city", "Denver")
        scroll_invoke_weather(city)
        return "ok"
    elif name == "get news":
        headlines = get_news_headlines(context.get("api_key", ""), context.get("topic", "technology"))
        for headline in headlines:
            print(f"[SCROLL] News Headline: {headline}")
        return "ok"
    else:
        print(f"[SCROLL] Unknown API scroll: {name}")
        return "unknown"
