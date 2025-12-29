# scarlet/conversation_mode.py

import os
import time
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
import threading

from threading import Event
from scarlet.tts import speak, is_speaking
from scarlet.config import SAMPLING_RATE
from scarlet.handler import handle_query, session_lang  # keep session_lang for forced language

# Try shared mic lock if present; otherwise fall back to a local lock
try:
    from scarlet.mic_lock import MIC_LOCK  # optional shared lock
except Exception:
    MIC_LOCK = threading.RLock()

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps

# ---- Load models once ----
print(" Loading Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

print(" Loading VAD model...")
vad_model = load_silero_vad()

# ---- Tunables ----
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = "int16"
INACTIVITY_TIMEOUT = 180  # 3 mins
VAD_THRESHOLD = 0.1
MIN_SILENCE_MS = 800
MIN_SPEECH_MS = 300
MAX_RECORD_SECONDS = 10
SPEECH_END_TIMEOUT = 1.0  # seconds of silence after speech end

def transcribe_with_whisper(audio_path, force_lang=None):
    if force_lang:
        segments, info = whisper_model.transcribe(audio_path, beam_size=5, task="transcribe", language=force_lang)
        language = force_lang
    else:
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)
        language = info.language

    print(f" Detected language: {language}")
    if language not in ["en", "te"]:
        print(" Ignoring non-English/Telugu speech.")
        return None

    full_text = " ".join([seg.text.strip() for seg in segments])
    return full_text.strip()

def record_until_speech(stop_event):
    """
    Opens the microphone, listens with VAD, and writes a temp WAV if speech is found.
    Entire mic usage is wrapped with MIC_LOCK to avoid PortAudio races with wake word.
    """
    q_audio = queue.Queue()
    raw_audio = []
    start_time = time.time()
    last_speech_time = None

    def callback(indata, frames, time_info, status):
        if status:
            print(" Stream status:", status)
        q_audio.put(indata.copy())

    # 🔒 Exclusively own the mic while the input stream is open
    with MIC_LOCK:
        try:
            with sd.InputStream(samplerate=SAMPLING_RATE, blocksize=BLOCK_SIZE, dtype=DTYPE,
                                channels=CHANNELS, callback=callback):
                print(" Listening for voice...")

                while not stop_event.is_set():
                    # timeout prevents busy-wait if queue is empty
                    try:
                        data = q_audio.get(timeout=0.2)
                        raw_audio.append(data)
                    except queue.Empty:
                        data = None

                    if data is not None:
                        flat_audio = np.concatenate(raw_audio, axis=0).flatten()
                        audio_float = flat_audio.astype(np.float32) / 32768.0
                        peak = np.max(np.abs(audio_float)) + 1e-6
                        audio_float /= peak

                        speech_ts = get_speech_timestamps(
                            audio_float,
                            vad_model,
                            sampling_rate=SAMPLING_RATE,
                            threshold=VAD_THRESHOLD,
                            min_silence_duration_ms=MIN_SILENCE_MS,
                            min_speech_duration_ms=MIN_SPEECH_MS,
                        )

                        if speech_ts:
                            last_speech_time = time.time()

                        if last_speech_time and (time.time() - last_speech_time > SPEECH_END_TIMEOUT):
                            print(" Silence after speech detected. Ending recording.")
                            break

                    if time.time() - start_time > MAX_RECORD_SECONDS:
                        print(" Max record time reached.")
                        break

            # After closing the stream, still under MIC_LOCK, decide whether we captured speech
            if not raw_audio:
                print(" No audio captured.")
                return None

            flat_audio = np.concatenate(raw_audio, axis=0).flatten()
            audio_float = flat_audio.astype(np.float32) / 32768.0
            peak = np.max(np.abs(audio_float)) + 1e-6
            audio_float /= peak

            # Final check for any speech at all
            speech_ts = get_speech_timestamps(
                audio_float,
                vad_model,
                sampling_rate=SAMPLING_RATE,
                threshold=VAD_THRESHOLD,
                min_silence_duration_ms=MIN_SILENCE_MS,
                min_speech_duration_ms=MIN_SPEECH_MS,
            )
            if not speech_ts:
                print(" No speech detected.")
                return None

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            try:
                sf.write(tmp.name, audio_float, SAMPLING_RATE)
                print(" Speech captured. Proceeding to transcribe...")
                return tmp.name
            finally:
                tmp.close()

        except sd.PortAudioError as e:
            # If the wake listener had the mic before, or any stale pointer remained,
            # ensure streams are stopped and allow a short pause.
            try:
                sd.stop()
            except Exception:
                pass
            print(f" PortAudio error while recording: {e}")
            time.sleep(0.2)
            return None

def conversation_mode(user="guest"):
    stop_event = Event()
    print(f" Conversation started as [{user}].")
    last_active = time.time()

    try:
        while True:
            # Ensure we don't capture while TTS is playing
            while is_speaking.is_set():
                time.sleep(0.1)

            if time.time() - last_active > INACTIVITY_TIMEOUT:
                print(" Inactive for 3 minutes. Exiting conversation mode.")
                break

            file_path = record_until_speech(stop_event)
            if not file_path:
                continue

            try:
                # Force Whisper language based on current session_lang, if set
                user_lang = session_lang.get(user, "en")
                force_lang = "te" if user_lang == "te" else None
                text = transcribe_with_whisper(file_path, force_lang=force_lang)
            except Exception as e:
                print(f" Transcription error: {e}")
                text = None
            finally:
                try:
                    os.remove(file_path)
                except Exception:
                    pass

            if not text:
                continue

            print(f" [{user}] said: {text}")
            if "scarlet stop" in text.lower():
                print(" 'Scarlet stop' detected. Exiting conversation mode.")
                break

            handle_query(text, user=user)
            last_active = time.time()

    except KeyboardInterrupt:
        print(" Interrupted. Exiting conversation mode.")

