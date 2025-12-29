# scarlet/wake_word.py

import time
from pocketsphinx import LiveSpeech
from scarlet.tts import is_speaking

# ✅ Wake word and sensitivity
WAKE_WORD = "scarlet"
SENSITIVITY = 1e-30  # Lower = more sensitive (try 1e-20, 1e-30)

# ✅ Initialize LiveSpeech detector once
speech = LiveSpeech(
    lm=False,
    keyphrase=WAKE_WORD,
    kws_threshold=SENSITIVITY,
    verbose=False
)

def init_porcupine():
    pass  # Retained for compatibility with main.py

def stop_porcupine():
    pass  # Retained for compatibility with main.py

def detect():
    """
    Blocks until a wake word is detected.
    Skips listening if Piper is currently speaking.
    """
    for phrase in speech:
        if is_speaking.is_set():
            time.sleep(0.1)
            continue

        # Ensure phrase has valid content (can happen with background noise)
        if WAKE_WORD.lower() in str(phrase).lower():
            print(f"✅ Detected wake word: {WAKE_WORD}")
            return True

    return False

