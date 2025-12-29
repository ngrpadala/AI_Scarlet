# scarlet/handler.py

import time
import math
import json
from scarlet.tts import speak
from scarlet.video_player import stop_loop
from scarlet.skills import handle_predefined, control_youtube, play_local
from scarlet.audio_io import record_audio
from scarlet.stt import transcribe
from scarlet.skills.whisper_mode import whisper_mode
from scarlet.llm_clients import chat_with_model
from scarlet.memory import remember_fact
from scarlet.memory_mood import (
    append_conversation,
    save_memory,
    log_akka_emotion,
    load_memory
)

# ✅ Load once at module level
memory = load_memory()

def load_greetings():
    try:
        with open("/home/nagapi5/scarlet/greetings.json") as f:
            return json.load(f)
    except:
        return {}

greetings = load_greetings()

# Global flags
current_user = "guest"
mistral_only = False

def handle_query(query: str):
    global mistral_only, current_user
    q = query.lower().strip()

    # Consent logic for Akka
    if current_user == "akka" and memory.get("akka_permission") == "pending":
        if any(w in q for w in ["yes", "okay", "sure"]):
            memory["akka_permission"] = "accepted"
            save_memory(memory)
            msg = greetings.get("akka", {}).get("if_accepted", "Thank you, Akka.")
            speak(msg)
            log_akka_emotion("consent", "Akka accepted the name", msg)
            return
        if "no" in q:
            memory["akka_permission"] = "denied"
            save_memory(memory)
            msg = greetings.get("akka", {}).get("if_denied", "That's okay.")
            speak(msg)
            log_akka_emotion("consent", "Akka denied the name", msg)
            return

    # Calculator mode
    if q.startswith("calculate"):
        expr = q.replace("calculate", "", 1).strip()
        try:
            result = eval(expr, {"__builtins__": None}, math.__dict__)
            speak(f"The answer is {result}")
        except Exception:
            speak("Sorry, I couldn’t compute that.")
        return

    # Switch between Groq/Mistral
    if "switch to mistral" in q:
        mistral_only = True
        speak("Safe mode activated: Mistral only.")
        return
    if "switch to groq" in q or "switch back" in q:
        mistral_only = False
        speak("Groq mode activated.")
        return

    # YouTube controls
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

    # Local playback
    if "play local" in q:
        stop_loop()
        if not play_local():
            speak("No media found.", with_video=False)
        return

    # Ask user for YouTube song
    if "play music" in q and "from youtube" not in q:
        stop_loop()
        speak("Which song?")
        time.sleep(0.2)
        record_audio()
        song = transcribe()
        q = f"play {song} from youtube"

    # Play music from YouTube
    if "play" in q and "from youtube" in q:
        stop_loop()
        song = q.replace("play", "").replace("from youtube", "").strip().rstrip(".?!")
        print(f"[DEBUG handle_query] YouTube branch hit with song: '{song}'")
        result = handle_predefined(f"play {song} from youtube")
        if result:
            speak(result, with_video=False)
        return

    # Whisper mode
    if "whisper mode" in q or "i need closeness" in q:
        stop_loop()
        whisper_mode(current_user)
        return

    # Predefined commands
    pre = handle_predefined(q)
    if pre:
        speak(pre)
        return

    # Send to LLM
    reply = chat_with_model(prompt=q, user_role=current_user, use_groq=not mistral_only)
    speak(reply)

    # Store in memory
    if not any(m in q for m in ["switch to mistral", "switch to groq", "switch back"]):
        append_conversation(query, reply)

    if current_user == "creator":
        remember_fact("naga", f"Said: {query}")

