# scarlet/skills/core.py

import subprocess
import json
from typing import Optional

from scarlet.config import MEDIA_DIR
from scarlet.skills.weather import get_weather  # keep on-demand weather
from scarlet.youtube_play import play_youtube_video


def handle_predefined(query: str) -> Optional[str]:
    q = query.lower().strip()
    if "hello" in q or "hi" in q:
        return "Hello! How can I help you?"
    if "who are you" in q:
        return "I'm Scarlet, your AI companion."
    if "weather" in q or "temperature" in q:
        return get_weather()
    return None

def play_local() -> bool:
    # (unchanged)
    try:
        import os, random
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

def play_youtube(query: str) -> None:
    """
    1) Fetch the real YouTube watch URL via yt-dlp JSON.
    2) Open it in the browser as a fallback to mpv streaming.
    """
    term = query.strip().rstrip(".?!")
    search = f"ytsearch1:{term}"

    # A) Get JSON info for top result
    try:
        raw = subprocess.check_output(
            ["yt-dlp", "-j", search],
            stderr=subprocess.DEVNULL,
            text=True
        ).splitlines()[0]
        info = json.loads(raw)
        watch = info.get("webpage_url") or info.get("url")
        print(f"[DEBUG play_youtube] watch URL → {watch}")
    except Exception as e:
        print(f"[ERROR play_youtube] yt-dlp -j failed: {e}")
        return

    # B) Try filtering through mpv first (optional)
    try:
        cmd = ["mpv", watch,
               "--fs", "--no-border", "--geometry=0:0",
               "--vf=scale=800:480,setsar=0.75"]
        print(f"[DEBUG play_youtube] trying mpv → {cmd}")
        p = subprocess.Popen(cmd,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        p.wait(timeout=2)
        if p.returncode == 0:
            print("[DEBUG play_youtube] mpv succeeded")
            return
        raise Exception("mpv exited")
    except Exception:
        print("[DEBUG play_youtube] mpv failed, falling back to browser")

    # C) Final fallback: open in default browser
    try:
        subprocess.Popen(["xdg-open", watch])
        print(f"[DEBUG play_youtube] opened in browser")
    except Exception as e:
        print(f"[ERROR play_youtube] xdg-open failed: {e}")

def control_youtube(action: str) -> None:
    # (unchanged)
    key_map = {"pause": "p", "resume": "p", "stop": "q"}
    key = key_map.get(action)
    if not key:
        return
    subprocess.run(["xdotool", "search", "--class", "mpv",
                    "windowactivate", "--sync"])
    subprocess.run(["xdotool", "key", key])
