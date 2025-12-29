
import os
import json


# === Absolute paths to your original working directory ===
DATA_DIR  = os.path.expanduser("~/scarlet")
VIDEO_DIR = os.path.join(DATA_DIR, "videos")
FACE_DIR  = os.path.join(DATA_DIR, "known_faces")

# === Other directories ===
BASE_DIR  = os.path.expanduser("~/porquipine")
MEDIA_DIR = os.path.expanduser("~/media")
AUDIO_DIR = os.path.expanduser("~/audio_files")

# === Wake word & audio paths ===
ACCESS_KEY_PATH   = os.path.join(BASE_DIR, "access_key.txt")
WAKE_WORD_FILE    = os.path.join(
    BASE_DIR, "Hey-Scarlet_en_raspberry-pi_v3_0_0.ppn"
)
AUDIO_RECORD_PATH = os.path.join(AUDIO_DIR, "input.wav")
#TEMP_WAV_PATH     = "/dev/shm/output.wav"
TEMP_WAV_PATH = "/dev/shm/input.wav"

# === Whisper & Piper model paths ===
WHISPER_CLI_PATH   = os.path.expanduser(
    "~/whisper_model/faster_whisper/whisper.cpp/build/bin/whisper-cli"
)
WHISPER_MODEL_PATH = os.path.expanduser(
    "~/whisper_model/faster_whisper/ggml-small.en.bin"
)
PIPER_MODEL_PATH = os.path.expanduser(
    "~/piper_voices/en/en_GB-jenny_dioco-medium.onnx"
    #"~/piper_voices/en/en_US-lessac-medium.onnx"
)

# === API keys loader ===
def _load_key(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

GROQ_API_KEY    = _load_key(
    os.path.expanduser("~/API_keys/Groq/groq.txt")
)

WEATHER_API_KEY = _load_key(
    os.path.expanduser("~/API_keys/weather/weather_api_key.txt")
)

NEWS_API_KEY = _load_key(os.path.expanduser("~/API_keys/news/news_api_key.txt"))


# === JSON profiles & memory paths ===
PERSONALITY_PATH   = os.path.join(DATA_DIR, "personality.json")
MOOD_PATH          = os.path.join(DATA_DIR, "scarlet_mood.json")
BEHAVIOR_PATH      = os.path.join(DATA_DIR, "behavior_rules.json")
MEMORY_PATH        = os.path.join(DATA_DIR, "scarlet_memory.json")
CONV_LOG_PATH      = os.path.join(DATA_DIR, "conversation_log.json")
ALARM_STORE_PATH  = os.path.join(DATA_DIR, "alarms_reminders.json")
CONVERSATION_LOG_PATH = os.path.join(DATA_DIR, "conversation_log.json")

# === JSON loader helper & initial loads ===
def load_json(path: str, default=None):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

personality    = load_json(PERSONALITY_PATH, {})
mood           = load_json(MOOD_PATH, {})
behavior_rules = load_json(BEHAVIOR_PATH, {})
memory         = load_json(MEMORY_PATH, {"naga": {"facts": []}})
CREATOR_NAME   = "naga"
# === Video expressions map ===
VIDEO_MAP = load_json(os.path.join(DATA_DIR, "video_map.json"), {})

# === Conversation mode tuning ===
CONVERSATION_TIMEOUT = 30  # seconds of silence to exit
VAD_THRESHOLD = 0.5        # silero default; you can tune later

SAMPLING_RATE = 16000  # Sample rate used for audio recording and VAD
TEMP_WAV_PATH = "/home/nagapi5/google_tts/output.wav"

