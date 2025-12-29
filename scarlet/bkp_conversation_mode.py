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

# Initialize Whisper model
print("🧠 Loading Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# Load VAD model
print("🔊 Loading VAD model...")
vad_model = load_silero_vad()

BLOCK_SIZE = 1024
CHANNELS = 1
dtype = "int16"
MAX_IDLE_TIME = 180  # 3 minutes

def transcribe_with_whisper(audio_path):
    segments, _ = whisper_model.transcribe(audio_path, beam_size=5)
    full_text = " ".join([seg.text.strip() for seg in segments])
    return full_text.strip()

def record_until_speech(stop_event, min_listen=10, max_wait=30):
    q_audio = queue.Queue()
    buffer = []
    start_time = time.time()

    def callback(indata, frames, time_info, status):
        if status:
            print("⚠️ Stream status:", status)
        q_audio.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLING_RATE, blocksize=BLOCK_SIZE, dtype=dtype,
                        channels=CHANNELS, callback=callback):
        while not stop_event.is_set():
            if not q_audio.empty():
                data = q_audio.get()
                buffer.append(data)

                audio_np = np.concatenate(buffer, axis=0).flatten().astype(np.float32) / 32768.0
                elapsed = time.time() - start_time

                if elapsed >= min_listen:
                    speech_ts = get_speech_timestamps(audio_np, vad_model, sampling_rate=SAMPLING_RATE)
                    if speech_ts:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                        temp_path = temp_file.name
                        sf.write(temp_path, audio_np, SAMPLING_RATE)
                        temp_file.close()
                        print("✅ Speech detected.")
                        return temp_path

                if max_wait is not None and elapsed > max_wait:
                    return None

def conversation_mode(user="guest"):
    stop_event = Event()
    last_activity_time = time.time()
    print("🎤 Scarlet is listening...")

    try:
        while True:
            while is_speaking.is_set():
                time.sleep(0.1)

            # Auto-exit if idle for 3 minutes
            if time.time() - last_activity_time > MAX_IDLE_TIME:
                print("⏳ Idle timeout. Returning to face detection.")
                return

            file_path = record_until_speech(stop_event, min_listen=10, max_wait=30)

            if file_path is None:
                print("🤫 No speech. Waiting for next input...")
                continue

            try:
                result = transcribe_with_whisper(file_path)
                os.remove(file_path)
            except Exception as e:
                print(f"❌ Whisper failed: {e}")
                continue

            if not result:
                print("🧭 Transcription was empty.")
                continue

            print(f"📝 Transcribed: {result}")
            last_activity_time = time.time()  # Reset idle timer
            handle_query(result)

    except KeyboardInterrupt:
        print("👋 Exiting conversation mode.")

