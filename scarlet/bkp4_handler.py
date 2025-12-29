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

# ✅ Load memory once
memory = load_memory()
session_lang = {}  # 🌐 Tracks per-session language by user

def load_greetings():
    try:
        with open("/home/nagapi5/scarlet/greetings.json") as f:
            return json.load(f)
    except:
        return {}

greetings = load_greetings()
mistral_only = False

def handle_query(query: str, user="guest"):
    global mistral_only, session_lang
    q = query.lower().strip()
    current_user = user

    # 🌐 Set default language if not set yet
    if current_user not in session_lang:
        session_lang[current_user] = "te" if current_user == "lalitha" else "en"

    lang = session_lang[current_user]

    # 🔄 Language switch
    if "speak in telugu" in q:
        session_lang[current_user] = "te"
        return speak("తెలుగులో మాట్లాడుతాను.", lang="te")

    if "speak in english" in q:
        session_lang[current_user] = "en"
        return speak("Switching back to English.", lang="en")

    # 🔒 Block personal/sensitive info for non-creators
    if current_user != "creator":
        restricted_keywords = [
            "whisper", "wife", "private", "intimate", "naga", "creator", "his lover", "his partner"
        ]
        if any(kw in q for kw in restricted_keywords):
            return speak("Sorry, I can't share that information.", lang=lang)

    # 🔒 Block system/behavior explanations for non-creators
    if current_user != "creator":
        system_queries = [
            "behavior rules", "how you work", "scarlet rules", "system design",
            "internal rules", "explain your behavior", "explain system"
        ]
        if any(kw in q for kw in system_queries):
            return speak("That information is restricted to my creator.", lang=lang)

    # Consent logic for Akka
    if current_user == "akka" and memory.get("akka_permission") == "pending":
        if any(w in q for w in ["yes", "okay", "sure"]):
            memory["akka_permission"] = "accepted"
            save_memory(memory)
            msg = greetings.get("akka", {}).get("if_accepted", "Thank you, Akka.")
            speak(msg, lang=lang)
            log_akka_emotion("consent", "Akka accepted the name", msg)
            return
        if "no" in q:
            memory["akka_permission"] = "denied"
            save_memory(memory)
            msg = greetings.get("akka", {}).get("if_denied", "That's okay.")
            speak(msg, lang=lang)
            log_akka_emotion("consent", "Akka denied the name", msg)
            return

    # Calculator
    if q.startswith("calculate"):
        expr = q.replace("calculate", "", 1).strip()
        try:
            result = eval(expr, {"__builtins__": None}, math.__dict__)
            speak(f"The answer is {result}", lang=lang)
        except Exception:
            speak("Sorry, I couldn’t compute that.", lang=lang)
        return

    # Groq/Mistral mode switch
    if "switch to mistral" in q:
        mistral_only = True
        speak("Safe mode activated: Mistral only.", lang=lang)
        return
    if "switch to groq" in q or "switch back" in q:
        mistral_only = False
        speak("Groq mode activated.", lang=lang)
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
            speak(f"{act.capitalize()}d YouTube.", with_video=False, lang=lang)
            return

    # Local audio
    if "play local" in q:
        stop_loop()
        if not play_local():
            speak("No media found.", with_video=False, lang=lang)
        return

    # Ask user for YouTube song
    if "play music" in q and "from youtube" not in q:
        stop_loop()
        speak("Which song?", lang=lang)
        time.sleep(0.2)
        record_audio()
        song = transcribe()
        q = f"play {song} from youtube"

    # Play from YouTube
    if "play" in q and "from youtube" in q:
        stop_loop()
        song = q.replace("play", "").replace("from youtube", "").strip().rstrip(".?!")
        print(f"[DEBUG handle_query] YouTube branch hit with song: '{song}'")
        result = handle_predefined(f"play {song} from youtube")
        if result:
            speak(result, with_video=False, lang=lang)
        return

    # Whisper mode
    if "whisper mode" in q or "i need closeness" in q:
        if current_user == "creator":
            stop_loop()
            whisper_mode(current_user)
        else:
            speak("This feature is only available for my creator.", lang=lang)
        return

    # Predefined responses
    pre = handle_predefined(q)
    if pre:
        speak(pre, lang=lang)
        return

    # LLM response (🧠 Inject Telugu response instruction if needed)
    prompt = f"Reply only in Telugu: {q}" if lang == "te" else q
    reply = chat_with_model(prompt=prompt, user_role=current_user, use_groq=not mistral_only)
    speak(reply, lang=lang)

    # Store conversation
    if not any(m in q for m in ["switch to mistral", "switch to groq", "switch back"]):
        append_conversation(query, reply)

    if current_user == "creator":
        remember_fact("naga", f"Said: {query}")

