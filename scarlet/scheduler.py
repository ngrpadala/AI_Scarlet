import os
import json
import time
import datetime
import schedule

from scarlet.config import ALARM_STORE_PATH
from scarlet.tts    import speak
from scarlet.logger import log
from scarlet.memory import summarize_memory

_alarms = []

def load_alarms():
    global _alarms
    if os.path.exists(ALARM_STORE_PATH):
        with open(ALARM_STORE_PATH, "r") as f:
            _alarms = json.load(f)
    else:
        _alarms = []
    log("scheduler", f"{len(_alarms)} alarms loaded.")

def save_alarms():
    with open(ALARM_STORE_PATH, "w") as f:
        json.dump(_alarms, f, indent=2)

def check_alarms():
    now = datetime.datetime.now().strftime("%H:%M")
    for alarm in list(_alarms):
        # alarm format: [time_str, message, label]
        if alarm[0] == now:
            speak(f"{alarm[2]}! {alarm[1]}")
            log("scheduler", f"Alarm triggered: {alarm[1]}")
            _alarms.remove(alarm)
            save_alarms()

def daily_briefing():
    """
    Morning summary without news/weather.
    """
    speak("Good morning! Here’s your summary of memories.")
    for line in summarize_memory():
        speak(line)

def run_scheduler():
    schedule.every().day.at("08:00").do(daily_briefing)
    while True:
        schedule.run_pending()
        time.sleep(10)

def monitor_temperature():
    while True:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                t = int(f.read().strip()) / 1000.0
            if t >= 70:
                speak(f"Warning, temperature is {int(t)}°C.")
                log("scheduler", f"High temp alert: {int(t)}°C")
        except:
            pass
        time.sleep(30)
