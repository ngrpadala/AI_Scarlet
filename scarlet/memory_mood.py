# scarlet/memory_mood.py

import json
import os
import time
from datetime import datetime
from scarlet.config import (
    PERSONALITY_PATH,
    MOOD_PATH,
    MEMORY_PATH,
    BEHAVIOR_PATH,
    CONVERSATION_LOG_PATH
)

AKKA_EMO_LOG_PATH = os.path.expanduser("~/scarlet/akka_emotions.json")
MOOD_STATE_PATH = os.path.expanduser("~/scarlet/memory_mood_state.json")

# 📁 General utilities
def load_json(path, default={}):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# 🧠 Base memory loading
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

# 📘 Akka emotion log
def log_akka_emotion(emotion, message, response):
    log = load_json(AKKA_EMO_LOG_PATH, [])
    log.append({
        "timestamp": datetime.now().isoformat(),
        "emotion": emotion,
        "message": message,
        "response": response
    })
    save_json(AKKA_EMO_LOG_PATH, log)

# ❤️ Mood state management (new)
def load_mood_state():
    return load_json(MOOD_STATE_PATH, {
        "current_mood": "neutral",
        "affection_score": 0,
        "last_affection_time": time.time()
    })

def save_mood_state(data):
    save_json(MOOD_STATE_PATH, data)

def reset_mood_state():
    data = {
        "current_mood": "neutral",
        "affection_score": 0,
        "last_affection_time": time.time()
    }
    save_mood_state(data)

def get_current_mood():
    return load_mood_state().get("current_mood", "neutral")

def set_mood(state):
    data = load_mood_state()
    data["current_mood"] = state
    save_mood_state(data)

def increase_affection_score(amount=1):
    data = load_mood_state()
    data["affection_score"] += amount
    data["last_affection_time"] = time.time()
    save_mood_state(data)

def decay_affection():
    data = load_mood_state()
    elapsed = time.time() - data.get("last_affection_time", time.time())
    decay = int(elapsed // 60)  # 1 point per minute
    if decay > 0:
        data["affection_score"] = max(0, data["affection_score"] - decay)
        data["last_affection_time"] = time.time()
        save_mood_state(data)

def should_escalate_romantic_mode(threshold=30):
    data = load_mood_state()
    return data.get("affection_score", 0) >= threshold

