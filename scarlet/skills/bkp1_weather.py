import requests
from scarlet.config import WEATHER_API_KEY

def get_weather(city: str = "Hyderabad", units: str = "metric") -> str:
    """
    Fetch current weather and brief forecast via OpenWeatherMap.
    Returns a detailed, human-readable summary.
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
        feels_like = data["main"]["feels_like"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        clouds = data["clouds"]["all"]
        desc = data["weather"][0]["description"]

        summary = (
            f"The weather in {city} is currently {desc} with a temperature of {temp}°C. "
            f"It feels like {feels_like}°C. The day's low is {temp_min}°C and high is {temp_max}°C. "
            f"Humidity is {humidity} percent, wind speed is {wind_speed} meters per second, "
            f"and cloud cover is {clouds} percent."
        )

        return summary

    except Exception as e:
        print(f"[weather] fetch error: {e}")
        return "Sorry, I couldn't fetch the weather."

