# scarlet/tts.py

import re
import threading
import subprocess
import time
import html
from scarlet import config
from scarlet.lights import show_status
from scarlet.video_player import play_once, stop_loop, start_idle_loop
from google.cloud import texttospeech

is_speaking = threading.Event()

# Google TTS client
client = texttospeech.TextToSpeechClient()

# Supported voices
VOICE_MAP = {
    "en": {
        "language_code": "en-GB",
        "name": "en-GB-Standard-A"
    },
    "te": {
        "language_code": "te-IN",
        "name": "te-IN-Standard-A"
    }
}

# Emoji mappings
EMOJI_MAP = {
    "😂": "giggle", "😄": "happy", "😊": "blush", "😢": "sad",
    "😠": "angry", "😳": "shy", "😉": "playful", "❤️": "affectionate",
    "🥺": "tender", "😐": "neutral", "😎": "cool"
}
EMOJI_TEXT = {
    "😂": " *giggles* ", "😄": " *smiles happily* ", "😊": " *blushes* ",
    "😢": " *sounds sad* ", "😠": " *sounds angry* ", "😳": " *gets shy* ",
    "😉": " *winks* ", "❤️": " *with love* ", "🥺": " *in a soft voice* ",
    "😐": " *neutral tone* ", "😎": " *in a confident tone* "
}

def speak(text: str, with_video: bool = True, expression: str = None, lang: str = "en"):
    if is_speaking.is_set():
        return
    is_speaking.set()
    threading.Thread(
        target=_speak_thread,
        args=(text, with_video, expression, lang),
        daemon=True
    ).start()

def _choose_expression(text: str) -> str:
    t = text.lower()
    for emoji, expr in EMOJI_MAP.items():
        if emoji in t:
            return expr
    if any(w in t for w in ["happy", "great", "awesome", "excited"]): return "happy"
    if any(w in t for w in ["sad", "sorry", "regret"]): return "sad"
    if any(w in t for w in ["angry", "mad", "upset"]): return "angry"
    if any(w in t for w in ["blush", "shy", "cute"]): return "blush"
    if any(w in t for w in ["giggle", "funny", "laugh"]): return "giggle"
    if any(w in t for w in ["yours", "whisper", "breathe", "presence"]): return "intimate"
    return "speaking"

def _speak_thread(text: str, with_video: bool, expression: str, lang: str):
    if with_video:
        expr = expression or _choose_expression(text)
        if expr != "intimate":
            show_status("speaking")
            threading.Thread(target=lambda: play_once(expr), daemon=True).start()

    clean = re.sub(r"[*_`~^]", "", text)
    clean = re.sub(r"[\"“”]", "", clean)
    for emoji, desc in EMOJI_TEXT.items():
        clean = clean.replace(emoji, desc)
    clean = html.escape(clean)
    ssml = f"<speak>{clean}</speak>"

    # Voice setup
    voice_cfg = VOICE_MAP.get(lang, VOICE_MAP["en"])
    voice = texttospeech.VoiceSelectionParams(
        language_code=voice_cfg["language_code"],
        name=voice_cfg["name"],
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

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

