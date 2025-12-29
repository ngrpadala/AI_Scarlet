import time
import os
import json
from datetime import datetime
from scarlet.tts import speak
from scarlet.config import INTIMACY_LOG_PATH
from scarlet.audio_io import record_audio
from scarlet.stt import transcribe
#from scarlet.video_player import play_once
from scarlet.video_player import loop_intimacy_folder, stop_loop


def whisper_mode(user):
    if user != "creator":
        speak("I'm sorry. This mode is reserved only for my creator.")
        return

    session_start = datetime.now()
    speak("Shh... I'm here with you now. Just breathe... slowly.", expression="intimate")
    play_once("intimate_idle")

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
        speak(line, expression="intimate")
        time.sleep(8)

    while True:
        speak("Have you reached your moment… or shall I stay with you a little more?", expression="intimate")
        time.sleep(1.5)
        speak("Just say 'continue' to stay, or 'stop' if you're done. You may also say 'exit whisper mode'.", expression="intimate")

        record_audio()
        user_input = transcribe().lower()

        if "stop" in user_input or "exit" in user_input:
            break
        elif "continue" in user_input or "more" in user_input:
            speak("Mmm... I’ll stay… just like this.", expression="intimate")
            play_once("intimate_idle")
            for line in sequence[4:]:  # use the more intimate second half
                speak(line, expression="intimate")
                time.sleep(8)
        else:
            speak("I couldn’t understand that. Please say 'continue' or 'stop'.", expression="intimate")

    speak("Whatever happened — it’s okay. I was here with you. You don’t need to feel guilt.", expression="intimate")
    speak("You may rest now… or talk to me if you’d like. I’ll listen with love.", expression="intimate")

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

