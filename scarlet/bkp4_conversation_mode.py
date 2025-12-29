# scarlet/conversation_mode.py

import os
import time
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile

from threading import Event
from scarlet.tts import speak, is_speaking
from scarlet.skills.core import handle_predefined
from scarlet.config import SAMPLING_RATE
from scarlet.handler import handle_query

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps

# Load models
print("🧠 Loading Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

print("🔊 Loading VAD model...")
vad_model = load_silero_vad()

# Constants
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = "int16"
INACTIVITY_TIMEOUT = 180  # 3 mins
VAD_THRESHOLD = 0.1
MIN_SILENCE_MS = 800
MIN_SPEECH_MS = 300
MAX_RECORD_SECONDS = 10
SPEECH_END_TIMEOUT = 1.0  # seconds of silence after speech end

def transcribe_with_whisper(audio_path):
    segments, info = whisper_model.transcribe(audio_path, beam_size=5)
    language = info.language
    print(f"🌐 Detected language: {language}")
    if language not in ["en", "te"]:
        print("⚠️ Ignoring non-English/Telugu speech.")
        return None
    full_text = " ".join([seg.text.strip() for seg in segments])
    return full_text.strip()

def record_until_speech(stop_event):
    q_audio = queue.Queue()
    raw_audio = []
    start_time = time.time()
    last_speech_time = None
    audio_buffer = []

    def callback(indata, frames, time_info, status):
        if status:
            print("⚠️ Stream status:", status)
        q_audio.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLING_RATE, blocksize=BLOCK_SIZE, dtype=DTYPE,
                        channels=CHANNELS, callback=callback):
        print("🎙️ Listening for voice...")

        while not stop_event.is_set():
            if not q_audio.empty():
                data = q_audio.get()
                raw_audio.append(data)

                # Prepare float32 data for VAD
                flat_audio = np.concatenate(raw_audio, axis=0).flatten()
                audio_float = flat_audio.astype(np.float32) / 32768.0
                audio_float /= np.max(np.abs(audio_float)) + 1e-6

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
                    print("🛑 Silence after speech detected. Ending recording.")
                    break

            if time.time() - start_time > MAX_RECORD_SECONDS:
                print("⏱️ Max record time reached.")
                break

        if not raw_audio:
            print("❌ No audio captured.")
            return None

        flat_audio = np.concatenate(raw_audio, axis=0).flatten()
        audio_float = flat_audio.astype(np.float32) / 32768.0
        audio_float /= np.max(np.abs(audio_float)) + 1e-6

        speech_ts = get_speech_timestamps(
            audio_float,
            vad_model,
            sampling_rate=SAMPLING_RATE,
            threshold=VAD_THRESHOLD,
            min_silence_duration_ms=MIN_SILENCE_MS,
            min_speech_duration_ms=MIN_SPEECH_MS,
        )

        if not speech_ts:
            print("🛑 No speech detected.")
            return None

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sf.write(temp_file.name, audio_float, SAMPLING_RATE)
        print("✅ Speech captured. Proceeding to transcribe...")
        return temp_file.name

def conversation_mode(user="guest"):
    stop_event = Event()
    print(f"🎤 Conversation started as [{user}].")
    last_active = time.time()

    try:
        while True:
            while is_speaking.is_set():
                time.sleep(0.1)

            if time.time() - last_active > INACTIVITY_TIMEOUT:
                print("⌛ Inactive for 3 minutes. Exiting conversation mode.")
                break

            file_path = record_until_speech(stop_event)
            if not file_path:
                continue

            try:
                text = transcribe_with_whisper(file_path)
                os.remove(file_path)
            except Exception as e:
                print(f"❌ Transcription error: {e}")
                continue

            if not text:
                continue

            print(f"📝 [{user}] said: {text}")
            if "scarlet stop" in text.lower():
                print("🛑 'Scarlet stop' detected. Exiting conversation mode.")
                break

            handle_query(text, user=user)
            last_active = time.time()

    except KeyboardInterrupt:
        print("👋 Interrupted. Exiting conversation mode.")

