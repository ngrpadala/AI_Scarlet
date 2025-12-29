import wave
import pyaudio
import subprocess
from scarlet.config import AUDIO_RECORD_PATH, WHISPER_MODEL_PATH

pa = pyaudio.PyAudio()

def record_audio(duration=5, rate=16000, path=AUDIO_RECORD_PATH):
    """Record `duration` seconds of audio to `path`."""
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=rate,
                     input=True,
                     frames_per_buffer=1024)
    frames = []
    for _ in range(int(rate / 1024 * duration)):
        frames.append(stream.read(1024, exception_on_overflow=False))
    stream.stop_stream()
    stream.close()

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))

def record_and_transcribe(duration=5):
    """
    Record audio for `duration` seconds and transcribe it using whisper.cpp.
    Returns the transcribed text.
    """
    record_audio(duration=duration)

    try:
        result = subprocess.run([
            "/home/nagapi5/whisper.cpp/main",         # path to whisper binary
            "-m", WHISPER_MODEL_PATH,                 # model file (e.g. ggml-small.en.bin)
            "-f", AUDIO_RECORD_PATH,                  # input .wav file
            "-otxt"
        ], capture_output=True, text=True, timeout=30)

        output_path = AUDIO_RECORD_PATH + ".txt"
        with open(output_path, "r") as f:
            return f.read().strip()

    except Exception as e:
        print(f"[STT Error] {e}")
        return ""

