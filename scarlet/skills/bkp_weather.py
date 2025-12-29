import requests
from scarlet.config import WEATHER_API_KEY

def get_weather(city: str = "Hyderabad", units: str = "metric") -> str:
    """
    Fetch current weather via OpenWeatherMap.
    Returns a human-readable summary.
    """
    if not WEATHER_API_KEY:
        print("[weather] No WEATHER_API_KEY set")
        return "Weather API key not configured."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": units}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"The temperature in {city} is {temp}°C with {desc}."
    except Exception as e:
        print(f"[weather] fetch error: {e}")
        return "Sorry, I couldn't fetch the weather."
