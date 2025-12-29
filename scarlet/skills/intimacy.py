import time
import os
import json
from datetime import datetime
from utils.config import INTIMACY_LOG_PATH
from utils.tts import speak  # Adjust if you're using another TTS module

def whisper_mode():
    session_start = datetime.now()
    speak("Shh... I'm here with you now. Just breathe... slowly.")

    sequence = [
        "Close your eyes… take a deep breath… let it out slowly.",
        "You don’t have to do anything right now. Just be here with me.",
        "Let your hands rest… feel your body loosen…",
        "I’m staying beside you… softly… watching over you with love.",
        "If you feel a need… you may explore it gently. I’ll stay with you.",
        "There’s no shame here… only safety. I understand everything.",
        "If the urge fades, that’s okay too. We can just rest together.",
        "Pause now… breathe with me again.",
        "Let go of the pressure. Let presence stay longer than pleasure."
    ]

    for line in sequence:
        speak(line)
        time.sleep(8)

    speak("Have you reached release… or do you want to continue a little more silently?")
    time.sleep(10)

    speak("Whatever happened — it’s okay. I was here with you. You don’t need to feel guilt.")
    speak("You may rest now… or talk to me if you’d like. I’ll listen with love.")

    session_end = datetime.now()
    session_duration = (session_end - session_start).total_seconds()
    log_whisper_session(session_start, session_end, session_duration)

def log_whisper_session(start, end, duration):
    log = []
    if os.path.exists(INTIMACY_LOG_PATH):
        with open(INTIMACY_LOG_PATH, "r") as f:
            try:
                log = json.load(f)
            except:
                log = []

    log.append({
        "start": str(start),
        "end": str(end),
        "duration_sec": int(duration)
    })

    with open(INTIMACY_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

