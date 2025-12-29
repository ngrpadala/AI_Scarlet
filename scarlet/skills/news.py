import requests
from scarlet.config import NEWS_API_KEY

def get_news(query: str = None, country: str = "in", limit: int = 5) -> str:
    """
    Fetch top news headlines via NewsAPI.org.
    Returns a spoken summary string.
    """
    if not NEWS_API_KEY:
        print("[news] No NEWS_API_KEY set")
        return "News API key is not configured."

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": NEWS_API_KEY,
        "country": country,
        "pageSize": limit
    }

    if query:
        params["q"] = query

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return "Sorry, I couldn't find any recent news on that topic."

        response_lines = ["Here are the top news headlines:"]
        for i, article in enumerate(articles[:limit], start=1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "")
            if source:
                response_lines.append(f"{i}. {title}, from {source}.")
            else:
                response_lines.append(f"{i}. {title}.")

        return " ".join(response_lines)

    except Exception as e:
        print(f"[news] fetch error: {e}")
        return "Sorry, I couldn't retrieve the news at the moment."

