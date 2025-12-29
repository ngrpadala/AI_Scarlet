import re
import threading
import subprocess
import time
from scarlet import config
from scarlet.lights import show_status
from scarlet.video_player import play_once, stop_loop, start_idle_loop
from google.cloud import texttospeech
import os

is_speaking = threading.Event()

# Google TTS client
client = texttospeech.TextToSpeechClient()

def speak(text: str, with_video: bool = True, expression: str = None):
    if is_speaking.is_set():
        return
    is_speaking.set()
    threading.Thread(target=_speak_thread, args=(text, with_video, expression), daemon=True).start()

def _choose_expression(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["happy", "great", "awesome", "excited"]): return "happy"
    if any(w in t for w in ["sad", "sorry", "regret"]): return "sad"
    if any(w in t for w in ["angry", "mad", "upset"]): return "angry"
    if any(w in t for w in ["blush", "shy", "cute"]): return "blush"
    if any(w in t for w in ["giggle", "funny", "laugh"]): return "giggle"
    if any(w in t for w in ["yours", "whisper", "breathe", "presence"]): return "intimate"
    return "speaking"

def _speak_thread(text: str, with_video: bool, expression: str = None):
    if with_video:
        expr = expression or _choose_expression(text)
        if expr != "intimate":
            show_status("speaking")
            threading.Thread(target=lambda: play_once(expr), daemon=True).start()

    # Build SSML
    safe_text = re.sub(r"[\"“”]", "", text)
    ssml = f"<speak>{safe_text}</speak>"

    # Configure voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB",
        name="en-GB-Standard-C",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    # Audio config
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    try:
        response = client.synthesize_speech(
            input=texttospeech.SynthesisInput(ssml=ssml),
            voice=voice,
            audio_config=audio_config
        )
        with open(config.TEMP_WAV_PATH, "wb") as out:
            out.write(response.audio_content)
        subprocess.run(["aplay", config.TEMP_WAV_PATH], check=True)
    except Exception as e:
        print("[TTS Error]:", e)

    stop_loop()
    show_status("idle")
    start_idle_loop()
    is_speaking.clear()

