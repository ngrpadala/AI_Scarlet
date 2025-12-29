import torch
import sounddevice as sd
import numpy as np
import tempfile
import os

# Load from Torch Hub
get_speech_timestamps = torch.hub.load("snakers4/silero-vad", "get_speech_timestamps", trust_repo=True)
read_audio = torch.hub.load("snakers4/silero-vad", "read_audio", trust_repo=True)
vad_model = torch.hub.load("snakers4/silero-vad", "load_model", trust_repo=True)

# Recording params
samplerate = 16000
duration = 3  # seconds

print("🎙️ Recording 3 seconds...")
recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
sd.wait()
print("✅ Recorded")

# Save to temp file in /dev/shm
temp_path = "/dev/shm/test_vad.wav"
sd.write(temp_path, recording, samplerate)

# Read and detect speech
print("🔍 Running VAD...")
audio_tensor = read_audio(temp_path, sampling_rate=samplerate)
speech_timestamps = get_speech_timestamps(audio_tensor, vad_model, sampling_rate=samplerate)

print("🟢 Speech timestamps:", speech_timestamps)

# Cleanup
os.remove(temp_path)

