# scarlet/scheduler.py

import os
import json
import time
import datetime
import threading

from scarlet.config import ALARM_STORE_PATH
from scarlet.logger import log
from scarlet.tts    import speak

# In‐memory list of alarms
alarms: list[dict] = []

def load_alarms():
    """
    Load alarms/reminders from disk at startup.
    Format of each alarm:
    {
      "time": "YYYY-MM-DD HH:MM",
      "message": "Your alarm text",
      "triggered": False
    }
    """
    global alarms
    if os.path.exists(ALARM_STORE_PATH):
        try:
            with open(ALARM_STORE_PATH, "r") as f:
                alarms = json.load(f)
        except Exception as e:
            log("scheduler", f"Failed to load alarms: {e}")
            alarms = []
    else:
        alarms = []
    log("scheduler", f"{len(alarms)} alarms loaded.")

def save_alarms():
    """
    Persist the current alarms list back to disk.
    """
    try:
        with open(ALARM_STORE_PATH, "w") as f:
            json.dump(alarms, f, indent=2)
    except Exception as e:
        log("scheduler", f"Failed to save alarms: {e}")

def run_scheduler():
    """
    Background thread stub for any repeating tasks.
    Currently does nothing but could be used for daily summaries, etc.
    """
    while True:
        # e.g. run a daily briefing at 07:00
        time.sleep(60)

def monitor_temperature():
    """
    Background thread stub for monitoring CPU/GPU temp.
    You can replace with real sensor‐reading code if desired.
    """
    while True:
        # e.g. if temp > threshold: speak or log
        time.sleep(300)

def check_alarms():
    """
    Called once per second in main loop.
    Triggers any alarms whose time has arrived.
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for alarm in alarms:
        if not alarm.get("triggered") and alarm.get("time") == now_str:
            msg = alarm.get("message", "Alarm")
            speak(msg)
            log("scheduler", f"Alarm triggered: {msg}")
            alarm["triggered"] = True
            save_alarms()
