import os
import json
from datetime import datetime
from scarlet.config import INTIMACY_LOG_PATH

def log_whisper_mode_session(start_time, end_time):
    """
    Record the session with start, end, duration (seconds & minutes), and timestamp.
    """
    session = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "start": datetime.fromtimestamp(start_time).strftime("%H:%M:%S"),
        "end": datetime.fromtimestamp(end_time).strftime("%H:%M:%S"),
        "duration_sec": int(end_time - start_time),
        "duration_min": round((end_time - start_time) / 60, 2)
    }

    log = []
    if os.path.exists(INTIMACY_LOG_PATH):
        try:
            with open(INTIMACY_LOG_PATH, "r") as f:
                log = json.load(f)
        except Exception as e:
            print("[Whisper Log Error]:", e)

    log.append(session)

    try:
        with open(INTIMACY_LOG_PATH, "w") as f:
            json.dump(log, f, indent=2)
        print("[Whisper Log] Session recorded successfully.")
    except Exception as e:
        print("[Whisper Log Save Error]:", e)

