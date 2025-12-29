# scarlet/logger.py

import os
import json
import time

from scarlet.config import CONV_LOG_PATH

def log(source: str, message: str):
    """
    Append a log entry with:
      - timestamp (YYYY-MM-DD HH:MM:SS)
      - source    (e.g. "scheduler", "llm_clients", etc.)
      - message   (any descriptive text)
    into the JSON array at CONV_LOG_PATH.
    """
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "source": source,
        "message": message
    }

    # Load existing logs (if any)
    logs = []
    if os.path.exists(CONV_LOG_PATH):
        try:
            with open(CONV_LOG_PATH, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    # Append and write back
    logs.append(entry)
    try:
        with open(CONV_LOG_PATH, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[logger] Error writing log: {e}")
