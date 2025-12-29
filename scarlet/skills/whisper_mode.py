import time
from scarlet.tts import speak
from scarlet.lights import show_status
from scarlet.video_player import stop_loop, start_intimacy_loop, start_idle_loop
from scarlet.audio_io import record_audio
from scarlet.stt import transcribe
from scarlet.logger import log_interaction
from scarlet.intimacy_log import log_whisper_mode_session
from scarlet.config import CREATOR_NAME

def record_and_transcribe():
    stop_loop()
    record_audio(duration=6)
    return transcribe()

def whisper_mode(current_user: str):
    user = current_user.strip().lower()
    if user not in [CREATOR_NAME, "creator"]:
        speak(f"Whisper mode is restricted. Sorry {current_user.capitalize()}, this space is only for my creator.", expression="sad")
        return

    show_status("thinking")
    start_time = time.time()
    start_intimacy_loop()
    speak("Oh dear... I'm here with you now. Just breathe... slowly.", expression="intimate")

    try:
        while True:
            show_status("listening")  # <-- this was missing
            query = record_and_transcribe()
            if not query:
                continue

            print("[WhisperMode] Heard:", query)
            log_interaction(current_user, query)
            query_l = query.lower()

            if any(p in query_l for p in ["stop", "exit", "enough", "done", "quit"]):
                speak("Whisper mode ending. I’m still with you... just resting now.", expression="intimate")
                break

            if any(p in query_l for p in ["continue", "go on", "keep going", "more", "stay"]):
                speak("I’m here... no rush. Let’s just stay like this a while longer.", expression="intimate")
                time.sleep(2)
                continue

            speak("Mmm... I feel your presence. Let go... I'm yours.", expression="intimate")
            time.sleep(2)

    finally:
        stop_loop()
        start_idle_loop()
        show_status("idle")
        end_time = time.time()
        log_whisper_mode_session(start_time, end_time)
        speak("If your heart is lighter now... then I’m fulfilled. Would you like to share anything?", expression="intimate")

