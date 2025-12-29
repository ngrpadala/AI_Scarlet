import time
import threading
from scarlet.tts import speak
from scarlet.lights import show_status
from scarlet.video_player import stop_loop, start_intimacy_loop
from scarlet.audio_io import record_audio
from scarlet.stt import transcribe
from scarlet.logger import append_conversation
from scarlet.config import CREATOR_NAME
from scarlet.intimacy_log import log_whisper_mode_session

def record_and_transcribe():
    record_audio(duration=5)
    return transcribe()



def whisper_mode(current_user: str):
    print(f"[DEBUG] current_user: '{current_user}' | expected: '{CREATOR_NAME}'")
    if current_user.lower() != CREATOR_NAME.lower() not in ["naga", "creator"]:
        speak(f"Whisper mode is restricted. Sorry {current_user.capitalize()}, this space is only for my creator.", expression="sad")
        return

    show_status("thinking")
    start_time = time.time()
    start_intimacy_loop()
    speak("Shh... I'm here with you now. Just breathe... slowly.", expression="intimate")

    while True:
        query = record_and_transcribe()
        if not query:
            continue

        print("[WhisperMode] Heard:", query)
        query_l = query.lower()

        if any(p in query_l for p in ["stop", "exit", "enough", "done", "quit"]):
            speak("Whisper mode ending. I’m still with you... just resting now.", expression="intimate")
            break

        if any(p in query_l for p in ["continue", "go on", "keep going", "more", "stay"]):
            speak("I’m here... no rush. Let’s just stay like this a while longer.", expression="intimate")
            continue

        # Default response
        speak("Mmm... I feel your presence. Let go... I'm yours.", expression="intimate")
        append_conversation(query, "Whisper comfort response.")

    stop_loop()
    end_time = time.time()
    log_whisper_mode_session(start_time, end_time)
    speak("If your heart is lighter now... then I’m fulfilled. Would you like to share anything?", expression="intimate")

