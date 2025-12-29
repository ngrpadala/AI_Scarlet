# save this as test_live_record.py
import sounddevice as sd
import numpy as np
import scipy.io.wavfile

SAMPLING_RATE = 16000
DURATION = 5  # seconds
OUTPUT_PATH = "/dev/shm/live_test.wav"

print(f"🎙️ Recording for {DURATION} seconds...")
audio = sd.rec(int(SAMPLING_RATE * DURATION), samplerate=SAMPLING_RATE, channels=1, dtype='int16')
sd.wait()
scipy.io.wavfile.write(OUTPUT_PATH, SAMPLING_RATE, audio)
print(f"✅ Audio saved to {OUTPUT_PATH}")

# optional playback
import os
os.system(f"aplay {OUTPUT_PATH}")

