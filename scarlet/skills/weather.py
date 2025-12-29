import requests
from datetime import datetime
from scarlet.config import WEATHER_API_KEY

def get_weather(city: str = "Hyderabad", units: str = "metric") -> str:
    """
    Fetch detailed weather via OpenWeatherMap.
    Returns a human-readable summary with short forecast.
    """
    if not WEATHER_API_KEY:
        print("[weather] No WEATHER_API_KEY set")
        return "Weather API key not configured."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": units
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        desc = data["weather"][0]["description"]
        main_weather = data["weather"][0]["main"].lower()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        sunrise_ts = data["sys"]["sunrise"]
        sunset_ts = data["sys"]["sunset"]

        sunrise = datetime.fromtimestamp(sunrise_ts).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p")

        forecast = ""
        if "rain" in main_weather or "shower" in desc:
            forecast = "You may expect rain today, please carry an umbrella."
        elif "snow" in main_weather:
            forecast = "Snowfall is possible today, stay warm and safe."
        elif "clear" in main_weather:
            forecast = "It looks like a clear day ahead."
        elif "cloud" in main_weather:
            forecast = "It might be cloudy but pleasant."

        return (
            f"The current weather in {city} is {desc} with a temperature of {temp}°C, "
            f"feels like {feels}°C. Humidity is {humidity} percent, and wind speed is {wind} meters per second. "
            f"The sun rises at {sunrise} and sets at {sunset}. {forecast}"
        )

    except Exception as e:
        print(f"[weather] fetch error: {e}")
        return "Sorry, I couldn't fetch the detailed weather."

