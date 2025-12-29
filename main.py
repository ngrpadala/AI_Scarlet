#!/usr/bin/env python3
import math
import threading
import time
import json
import os

from scarlet.tts               import speak, is_speaking
from scarlet.video_player      import start_loop, stop_loop, play_once
from scarlet.lights            import clear_ring, show_status
from scarlet.face_recognition  import detect_face
from scarlet.skills            import (
    handle_predefined,
    control_youtube,
    play_local,
)
from scarlet.llm_clients       import chat_with_model
from scarlet.memory            import remember_fact
from scarlet.audio_io          import record_audio
from scarlet.stt               import transcribe
from scarlet.wake_word         import detect  # ✅ Only detect needed now
from scarlet.skills.whisper_mode import whisper_mode
from scarlet.conversation_mode import conversation_mode
from scarlet.handler           import handle_query
import scarlet.scheduler       as scheduler
from scarlet.memory_mood       import (
    load_personality,
    load_mood,
    load_memory,
    save_memory,
    append_conversation,
    log_akka_emotion,
)

current_user = "guest"
mistral_only = False
personality   = load_personality()
mood          = load_mood()
memory        = load_memory()

def load_greetings():
    try:
        with open("/home/nagapi5/scarlet/greetings.json") as f:
            return json.load(f)
    except:
        return {}

greetings = load_greetings()

def greet_user(name):
    global current_user

    if name == "naga":
        current_user = "creator"
        return greetings.get("creator", {}).get("general", "Hello Naga.")

    if name == "lalitha":
        current_user = "akka"
        g = greetings.get("akka", {})
        perm = memory.get("akka_permission")

        if perm == "accepted":
            msg = g.get("if_accepted", "Hi Akka, how are you feeling?")
            log_akka_emotion("greeting", "Scarlet greeted Akka (accepted)", msg)
            return msg

        if perm == "denied":
            msg = g.get("if_denied", "I'm always here for you.")
            log_akka_emotion("greeting", "Scarlet greeted Akka (denied)", msg)
            return msg

        memory["akka_permission"] = "pending"
        save_memory(memory)
        msg = g.get("ask_permission", "Can I call you Akka?")
        log_akka_emotion("greeting", "Scarlet asked Akka for permission", msg)
        return msg

    current_user = "guest"
    return "Hi there"

def wake_loop():
    global current_user

    while True:
        if detect():
            stop_loop()
            play_once("namaste")
            show_status("listening")

            name = detect_face().lower()
            greet = greet_user(name)
            speak(greet)

            while is_speaking.is_set():
                time.sleep(0.2)

            show_status("thinking")
            conversation_mode(current_user)

            while is_speaking.is_set():
                time.sleep(0.2)

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

