# scarlet/skills/core.py

import subprocess
import json
import os
import random
from typing import Optional
from scarlet.tts import speak
from scarlet.config import MEDIA_DIR
from scarlet.skills.weather import get_weather  # keep on-demand weather
from scarlet.youtube_play import play_youtube_video  # new working version


def handle_predefined(query: str) -> Optional[str]:
    q = query.lower().strip()
    if "hello" in q or "hi" in q:
        return "Hello! How can I help you?"
    if "who are you" in q:
        return "I'm Scarlet, your AI companion."
    if "weather" in q or "temperature" in q:
        return get_weather()
    if "play" in q and "youtube" in q:
        # Extract the actual search query
        query_term = q.replace("play", "").replace("on youtube", "").strip()
        speak(f"Searching YouTube for {query_term}")
        result = play_youtube_video(f"ytsearch:{query_term}")
        speak(result)
        return result
    return None


def play_local() -> bool:
    try:
        files = [f for f in os.listdir(MEDIA_DIR)
                 if f.lower().endswith((".mp3", ".wav", ".mp4"))]
        if not files:
            return False
        choice = random.choice(files)
        subprocess.Popen(
            ["mpv", os.path.join(MEDIA_DIR, choice)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except:
        return False


def control_youtube(action: str) -> None:
    key_map = {"pause": "p", "resume": "p", "stop": "q"}
    key = key_map.get(action)
    if not key:
        return
    subprocess.run(["xdotool", "search", "--class", "mpv",
                    "windowactivate", "--sync"])
    subprocess.run(["xdotool", "key", key])


# ✅ NEW FUNCTION: Used in conversation_mode.py
def handle_query(query: str) -> str:
    query = query.strip().lower()

    # Try predefined responses
    predefined = handle_predefined(query)
    if predefined:
        return predefined

    # Simple fallback
    if "your name" in query:
        return "My name is Scarlet, your assistant."
    elif "how are you" in query:
        return "I'm doing well, thank you for asking!"
    elif "today" in query:
        from datetime import datetime
        return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."
    else:
        return f"You said: {query}"

