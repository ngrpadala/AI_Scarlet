from faster_whisper import WhisperModel

# ✅ Load from local model directory
model = WhisperModel("/home/nagapi5/models/faster-whisper/base", device="cpu", compute_type="int8")

# ✅ Transcribe test file
segments, info = model.transcribe("/dev/shm/test.wav", beam_size=1)

print("Detected language:", info.language)
print("Transcription segments:")
for segment in segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")

