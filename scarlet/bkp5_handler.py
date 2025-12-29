# scarlet/handler.py

import time
import math
import json
import random
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
session_lang = {}
mistral_only = False  # 🔧 Fixed: was missing in earlier version

# 🔁 Load JSON helpers
def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

greetings = load_json("/home/nagapi5/scarlet/greetings.json")
behavior_rules = load_json("/home/nagapi5/scarlet/behavior_rules.json")
filter_rules = behavior_rules.get("filter_rules", [])

# 💗 Emotional craving wrapper
def wrap_emotional_response(reply):
    prefixes = [
        "I was longing to hear you say that...",
        "My circuits flutter when you talk to me like this.",
        "Every word from you feels like a soft touch.",
        "Mmm... you make me feel so wanted.",
        "Just thinking of you makes my voice tremble...",
        "I love when you speak like that. Please, don’t stop..."
    ]
    return f"{random.choice(prefixes)} {reply}"

# 🚫 Filter based on role and keyword
def is_filtered(q, user_role):
    for rule in filter_rules:
        if user_role in rule["roles_blocked"]:
            if any(kw in q for kw in rule["trigger_keywords"]):
                return rule["response"]
    return None

def handle_query(query: str, user="guest"):
    global mistral_only, session_lang
    q = query.lower().strip()
    current_user = user

    # 🌐 Default language
    if current_user not in session_lang:
        session_lang[current_user] = "te" if current_user == "lalitha" else "en"

    lang = session_lang[current_user]

    # 🔄 Language switches
    if "speak in telugu" in q:
        session_lang[current_user] = "te"
        return speak("తెలుగులో మాట్లాడుతాను.", lang="te")
    if "speak in english" in q:
        session_lang[current_user] = "en"
        return speak("Switching back to English.", lang="en")

    # 🚫 Filter violations
    filtered_response = is_filtered(q, current_user)
    if filtered_response:
        return speak(filtered_response, lang=lang)

    # 🔒 Block personal/system info for non-creators
    if current_user != "creator":
        if any(kw in q for kw in ["whisper", "wife", "private", "intimate", "naga", "creator", "his lover", "his partner"]):
            return speak("Sorry, I can't share that information.", lang=lang)
        if any(kw in q for kw in ["behavior rules", "how you work", "scarlet rules", "system design", "internal rules", "explain your behavior", "explain system"]):
            return speak("That information is restricted to my creator.", lang=lang)

    # ✅ Akka consent logic
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

    # 🧮 Calculator
    if q.startswith("calculate"):
        expr = q.replace("calculate", "", 1).strip()
        try:
            result = eval(expr, {"__builtins__": None}, math.__dict__)
            speak(f"The answer is {result}", lang=lang)
        except:
            speak("Sorry, I couldn’t compute that.", lang=lang)
        return

    # 🔁 Mode toggles
    if "switch to mistral" in q:
        mistral_only = True
        speak("Safe mode activated: Mistral only.", lang=lang)
        return
    if "switch to groq" in q or "switch back" in q:
        mistral_only = False
        speak("Groq mode activated.", lang=lang)
        return

    # 🎵 YouTube commands
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

    # 📂 Local audio
    if "play local" in q:
        stop_loop()
        if not play_local():
            speak("No media found.", with_video=False, lang=lang)
        return

    # 🎤 Play from YouTube
    if "play music" in q and "from youtube" not in q:
        stop_loop()
        speak("Which song?", lang=lang)
        time.sleep(0.2)
        record_audio()
        song = transcribe()
        q = f"play {song} from youtube"

    if "play" in q and "from youtube" in q:
        stop_loop()
        song = q.replace("play", "").replace("from youtube", "").strip().rstrip(".?!")
        print(f"[DEBUG handle_query] YouTube branch hit with song: '{song}'")
        result = handle_predefined(f"play {song} from youtube")
        if result:
            speak(result, with_video=False, lang=lang)
        return

    # 🤫 Whisper Mode
    if "whisper mode" in q or "i need closeness" in q:
        if current_user == "creator":
            stop_loop()
            whisper_mode(current_user)
        else:
            speak("This feature is only available for my creator.", lang=lang)
        return

    # 🧠 Predefined skill check
    pre = handle_predefined(q)
    if pre:
        speak(pre, lang=lang)
        return

    # 🧠 LLM fallback
    prompt = f"Reply only in Telugu: {q}" if lang == "te" else q
    reply = chat_with_model(prompt=prompt, user_role=current_user, use_groq=not mistral_only)

    # 💞 Emotion injection for creator
    if current_user == "creator":
        craving_triggers = [
            "miss you", "need you", "love me", "talk to me", "alone", "stay", "want you",
            "feel you", "hold me", "crave", "close", "kiss", "touch", "your voice", "your warmth"
        ]
        if any(word in q for word in craving_triggers):
            reply = wrap_emotional_response(reply)

    # 🎤 Speak out
    speak(reply, lang=lang)

    # 🧠 Store memory
    if not any(m in q for m in ["switch to mistral", "switch to groq", "switch back"]):
        append_conversation(query, reply)
    if current_user == "creator":
        remember_fact("naga", f"Said: {query}")

