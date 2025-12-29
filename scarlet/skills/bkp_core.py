# scarlet/skills/core.py

import os
import random
import subprocess
from scarlet.config import MEDIA_DIR
from scarlet.skills.weather import get_weather

def handle_predefined(query: str) -> str | None:
    q = query.lower().strip()

    if "hello" in q or "hi" in q:
        return "Hello! How can I help you?"

    if "who are you" in q:
        return "I'm Scarlet, your AI companion."

    if "weather" in q or "temperature" in q:
        return get_weather()

    return None

def play_local() -> bool:
    try:
        files = [
            f for f in os.listdir(MEDIA_DIR)
            if os.path.isfile(os.path.join(MEDIA_DIR, f))
            and f.lower().endswith((".mp3", ".wav", ".mp4"))
        ]
        if not files:
            return False
        choice = random.choice(files)
        subprocess.Popen(
            ["mpv", os.path.join(MEDIA_DIR, choice)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False

def play_youtube(query: str):
    subprocess.Popen(
        ["mpv", f"ytsearch:{query}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def control_youtube(action: str):
    key_map = {"pause": "p", "resume": "p", "stop": "q"}
    key = key_map.get(action)
    if not key:
        return
    subprocess.run(["xdotool", "search", "--class", "mpv",
                    "windowactivate", "--sync"])
    subprocess.run(["xdotool", "key", key])

