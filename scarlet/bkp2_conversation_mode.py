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
from scarlet.handler import handle_query  # ✅ will now accept user

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps

# Initialize Whisper model once
print("🧠 Loading Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# Load Silero VAD
print("🔊 Loading VAD model...")
vad_model = load_silero_vad()

# Streaming parameters
BLOCK_SIZE = 1024
CHANNELS = 1
dtype = "int16"
INACTIVITY_TIMEOUT = 180  # 3 minutes


def transcribe_with_whisper(audio_path):
    segments, _ = whisper_model.transcribe(audio_path, beam_size=5)
    full_text = " ".join([seg.text.strip() for seg in segments])
    return full_text.strip()


def record_until_speech(stop_event, min_listen=3, max_wait=20):
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
                audio_np /= np.max(np.abs(audio_np)) + 1e-6  # Normalize

                elapsed = time.time() - start_time

                if elapsed >= min_listen:
                    speech_ts = get_speech_timestamps(audio_np, vad_model,
                                                      sampling_rate=SAMPLING_RATE,
                                                      threshold=0.3)
                    if speech_ts:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                        temp_path = temp_file.name
                        sf.write(temp_path, audio_np, SAMPLING_RATE)
                        temp_file.close()
                        print("✅ Speech detected. Transcribing...")
                        return temp_path

                if max_wait is not None and elapsed > max_wait:
                    print("⏳ No speech detected for a while. Skipping.")
                    return None


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

            print("🎙️ Listening...")
            file_path = record_until_speech(stop_event, min_listen=3, max_wait=20)

            if file_path is None:
                print("❌ No speech. Waiting for next input...\n")
                continue

            try:
                result = transcribe_with_whisper(file_path)
                os.remove(file_path)
            except Exception as e:
                print(f"❌ Whisper failed: {e}")
                continue

            if not result:
                print("❌ Transcription empty.")
                continue

            print(f"📝 [{user}] said: {result}")
            handle_query(result, user=user)  # ✅ Pass correct user identity
            last_active = time.time()

    except KeyboardInterrupt:
        print("👋 Exiting conversation mode.")

