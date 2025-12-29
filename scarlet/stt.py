import subprocess
from scarlet.config import WHISPER_CLI_PATH, WHISPER_MODEL_PATH, AUDIO_RECORD_PATH

def transcribe():
    """Run Whisper CLI on last-recorded WAV and return lowercase text."""
    try:
        subprocess.run([
            WHISPER_CLI_PATH,
            "-m", WHISPER_MODEL_PATH,
            "-f", AUDIO_RECORD_PATH,
            "-otxt"
        ], check=True)
        with open(AUDIO_RECORD_PATH + ".txt") as f:
            return f.read().strip().lower()
    except Exception as e:
        print("[Whisper Error]:", e)
        return ""
