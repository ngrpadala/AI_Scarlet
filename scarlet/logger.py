import os
import json
import datetime

from scarlet.config import CONV_LOG_PATH

def log_interaction(role: str, text: str):
    """
    Append a conversation entry to CONV_LOG_PATH.
    """
    if not os.path.exists(CONV_LOG_PATH):
        with open(CONV_LOG_PATH, "w") as f:
            json.dump([], f)

    try:
        with open(CONV_LOG_PATH, "r") as f:
            logs = json.load(f)
    except Exception:
        logs = []

    logs.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "role": role,
        "text": text
    })

    with open(CONV_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

# Alias for backward compatibility
def log(source: str, message: str):
    log_interaction(source, message)

# New function for Whisper Mode compatibility
def append_conversation(user_input, assistant_response):
    if not os.path.exists(CONV_LOG_PATH):
        with open(CONV_LOG_PATH, "w") as f:
            json.dump([], f)

    try:
        with open(CONV_LOG_PATH, "r") as f:
            log = json.load(f)
    except Exception:
        log = []

    log.append({
        "user": user_input,
        "assistant": assistant_response
    })

    with open(CONV_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

