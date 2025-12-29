import json
import os
from datetime import datetime
from scarlet.config import (
    PERSONALITY_PATH,
    MOOD_PATH,
    MEMORY_PATH,
    BEHAVIOR_PATH,
    CONVERSATION_LOG_PATH
)

AKKA_EMO_LOG_PATH = os.path.expanduser("~/scarlet/akka_emotions.json")

def load_json(path, default={}):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_personality():
    return load_json(PERSONALITY_PATH)

def load_mood():
    return load_json(MOOD_PATH)

def load_memory():
    return load_json(MEMORY_PATH)

def save_memory(memory):
    save_json(MEMORY_PATH, memory)

def load_behavior_rules():
    return load_json(BEHAVIOR_PATH, {"core_rules": []})

def load_conversation_log():
    return load_json(CONVERSATION_LOG_PATH, [])

def append_conversation(user, assistant):
    log = load_conversation_log()
    log.append({"user": user, "assistant": assistant})
    save_json(CONVERSATION_LOG_PATH, log)

def log_akka_emotion(emotion, message, response):
    """Logs emotional interactions related to Akka."""
    log = load_json(AKKA_EMO_LOG_PATH, [])
    log.append({
        "timestamp": datetime.now().isoformat(),
        "emotion": emotion,
        "message": message,
        "response": response
    })
    save_json(AKKA_EMO_LOG_PATH, log)

