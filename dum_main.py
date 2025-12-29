#!/usr/bin/env python3
import math
import threading
import time

from scarlet.tts              import speak, is_speaking
from scarlet.video_player     import start_loop, stop_loop, play_once
from scarlet.wake_word        import detect
from scarlet.lights           import clear_ring, show_status
from scarlet.face_recognition import detect_face

from scarlet.skills.core      import (
    handle_predefined,
    play_local,
    play_youtube,
    control_youtube
)
from scarlet.skills.news      import get_news
from scarlet.skills.weather   import get_weather

from scarlet.llm_clients      import chat_with_model
from scarlet.memory           import remember_fact
from scarlet.audio_io         import record_audio
from scarlet.stt              import transcribe
import scarlet.scheduler      as scheduler

current_user = "guest"
mistral_only = False

def handle_query(query: str):
    global mistral_only
    q = query.lower().strip()

    # 1) Math
    if q.startswith("calculate"):
        expr = q.replace("calculate", "", 1).strip()
        try:
            result = eval(expr, {"__builtins__": None}, math.__dict__)
            speak(f"The answer is {result}")
        except Exception:
            speak("Sorry, I couldn’t compute that.")
        return

    # 2) LLM toggle
    if "switch to mistral" in q:
        mistral_only = True
        speak("Safe mode activated: Mistral only.")
        return
    if "switch to groq" in q:
        mistral_only = False
        speak("Groq mode activated.")
        return

    # 3) YouTube controls
    for cmd, act in {
        "pause youtube":  "pause",
        "resume youtube": "resume",
        "stop youtube":   "stop"
    }.items():
        if cmd in q:
            stop_loop()
            control_youtube(act)
            speak(f"{act.capitalize()}d YouTube.", with_video=False)
            return

    # 4) Local media
    if "play local" in q:
        stop_loop()
        if not play_local():
            speak("No media found.", with_video=False)
        return

    # 5) Music follow-up
    if "play music" in q and "from youtube" not in q:
        stop_loop()
        speak("Which song?")
        time.sleep(0.2)
        record_audio()
        song = transcribe()
        q = f"play {song} from youtube"

    # 6) YouTube play
    if "play" in q and "from youtube" in q:
        stop_loop()
        song = q.replace("play", "").replace("from youtube", "").strip()
        speak(f"Playing {song}.", with_video=False)
        play_youtube(song)
        start_loop("idle")
        return

    # 7) News
    if any(w in q for w in ["news", "headlines", "updates", "current events"]):
        stop_loop()
        topic = None
        if "about" in q:
            topic = q.split("about", 1)[-1].strip()
        elif "on" in q:
            topic = q.split("on", 1)[-1].strip()

        headlines = get_news(query=topic)
        if headlines:
            intro = (
                f"Here are the latest headlines about {topic}."
                if topic else
                "Here are the top news headlines."
            )
            speak(intro, with_video=False)
            for title in headlines:
                speak(title, with_video=False)
        else:
            speak("Sorry, I couldn't fetch any news right now.", with_video=False)
        start_loop("idle")
        return

    # 8) Weather
    if "weather" in q or "temperature" in q:
        stop_loop()
        city = "Hyderabad"
        if "in" in q:
            city = q.split("in", 1)[-1].strip()
        summary = get_weather(city)
        speak(summary, with_video=False)
        start_loop("idle")
        return

    # 9) Predefined
    pre = handle_predefined(q)
    if pre:
        speak(pre)
        return

    # 10) LLM fallback
    reply = chat_with_model(
        prompt=q,
        user_role=current_user,
        use_groq=not mistral_only
    )
    speak(reply)

    # 11) Memory (creator only)
    if current_user == "creator":
        remember_fact("naga", f"Said: {query}")

def wake_loop():
    global current_user
    while True:
        if detect():
            stop_loop()
            play_once("namaste")
            show_status("listening")

            name = detect_face()
            current_user = "creator" if name == "naga" else "guest"
            greet = "Hello Naga" if current_user == "creator" else "Hi there"
            speak(f"{greet}, how can I assist you?")

            while is_speaking.is_set():
                time.sleep(0.1)

            show_status("thinking")
            record_audio()
            q = transcribe()
            if q:
                handle_query(q)
            else:
                speak("Sorry, I didn't catch that.")

            clear_ring()
            start_loop("idle")

if __name__ == "__main__":
    scheduler.load_alarms()
    start_loop("idle")
    speak("Scarlet is now online and ready.")

    threading.Thread(target=wake_loop, daemon=True).start()
    threading.Thread(target=scheduler.monitor_temperature, daemon=True).start()
    threading.Thread(target=scheduler.run_scheduler, daemon=True).start()

    try:
        while True:
            scheduler.check_alarms()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Exit] Shutting down Scarlet...")
    finally:
        clear_ring()
        stop_loop()
