# scarlet/wake_word.py

import time
import threading
import sounddevice as sd
from pocketsphinx import LiveSpeech
from scarlet.tts import is_speaking

# Try shared mic lock if present; otherwise fall back to a local lock
try:
    from scarlet.mic_lock import MIC_LOCK  # optional shared lock
except Exception:
    MIC_LOCK = threading.RLock()

# ✅ File paths / config
HMM_PATH = "/home/nagapi5/pocketsphinx-model/cmusphinx-en-us-5.2"
DICT_PATH = "/home/nagapi5/pocketsphinx-model/cmusphinx-en-us-5.2/cmudict-en-us.dict"
WAKE_WORD = "scarlet"
THRESHOLD = 1e-30  # Lower = more sensitive (adjust as needed)

def _make_speech():
    # Recreate a fresh LiveSpeech every attempt (prevents stale PortAudio stream pointers)
    return LiveSpeech(
        hmm=HMM_PATH,
        dict=DICT_PATH,
        keyphrase=WAKE_WORD,
        kws_threshold=THRESHOLD,
        verbose=False,
        # audio_device='hw:1,0',  # uncomment & set if you need a specific input device
    )

def init_porcupine():
    pass  # compatibility with main.py

def stop_porcupine():
    pass

def detect():
    """
    Blocks until the wake word is detected.
    Uses a mic lock to prevent clashes with conversation_mode.
    Auto-recovers from PortAudio 'Invalid stream pointer' (-9988) by recreating the stream.
    """
    backoff = 0.2
    while True:
        # If TTS is talking, don't sit on the mic; wait briefly.
        if is_speaking.is_set():
            time.sleep(0.1)
            continue

        # Exclusively claim the microphone while listening for wake word.
        with MIC_LOCK:
            try:
                # Opening LiveSpeech (which opens a PortAudio InputStream) inside the lock.
                for phrase in _make_speech():
                    if is_speaking.is_set():
                        # If TTS starts mid-listen, yield quickly
                        time.sleep(0.1)
                        break

                    spoken = str(phrase).strip().lower()
                    if not spoken:
                        continue

                    if WAKE_WORD in spoken:
                        print(f"✅ Wake word detected: {spoken}")
                        return True

                # If we exit the for-loop without returning, loop and retry.
                backoff = 0.2  # reset backoff on a clean cycle

            except sd.PortAudioError as e:
                # Typical after another component used the mic: -9988 Invalid stream pointer
                try:
                    sd.stop()  # stop any dangling streams
                except Exception:
                    pass
                time.sleep(backoff)
                backoff = min(backoff * 2, 2.0)  # small exponential backoff
            except Exception:
                # Be resilient to any unexpected error
                time.sleep(0.2)

