# scarlet/wake_word.py

import time
from pocketsphinx import LiveSpeech
from scarlet.tts import is_speaking

# ✅ File paths
HMM_PATH = "/home/nagapi5/pocketsphinx-model/cmusphinx-en-us-5.2"
DICT_PATH = "/home/nagapi5/pocketsphinx-model/cmusphinx-en-us-5.2/cmudict-en-us.dict"
WAKE_WORD = "scarlet"
THRESHOLD = 1e-30  # Lower = more sensitive (adjust as needed)

# ✅ Initialize LiveSpeech with acoustic model + dict + keyphrase
speech = LiveSpeech(
    hmm=HMM_PATH,
    dict=DICT_PATH,
    keyphrase=WAKE_WORD,
    kws_threshold=THRESHOLD,
    verbose=False
)

def init_porcupine():
    pass  # For compatibility with main.py

def stop_porcupine():
    pass

def detect():
    """
    Blocks until the wake word is detected.
    Skips listening if Scarlet is currently speaking.
    """
    for phrase in speech:
        if is_speaking.is_set():
            time.sleep(0.1)
            continue

        spoken = str(phrase).strip().lower()
        if WAKE_WORD in spoken:
            print(f"✅ Wake word detected: {spoken}")
            return True

    return False

