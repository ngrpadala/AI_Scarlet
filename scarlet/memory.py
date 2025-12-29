import os
import json
import datetime

from scarlet.config import MEMORY_PATH

MAX_CTX = 5
_history = []

def update_conversation(role, text):
    _history.append((role, text))
    if len(_history) > MAX_CTX * 2:
        _history.pop(0)

def get_conversation_history():
    return [{"role": r, "content": t} for r, t in _history]

def remember_fact(user, fact):
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH) as f:
                mem = json.load(f)
        except:
            mem = {}
    else:
        mem = {}

    entry = mem.get(user)
    if not isinstance(entry, dict):
        entry = {"facts": []}
    facts = entry.get("facts")
    if not isinstance(facts, list):
        if isinstance(facts, str):
            facts = [{"text": facts, "date": None}]
        else:
            facts = []

    normalized = []
    for item in facts:
        if isinstance(item, dict) and "text" in item:
            normalized.append({
                "text": item["text"],
                "date": item.get("date")
            })

    if not any(f["text"] == fact for f in normalized):
        normalized.append({
            "text": fact,
            "date": datetime.date.today().isoformat()
        })

    mem[user] = {"facts": normalized}
    with open(MEMORY_PATH, "w") as f:
        json.dump(mem, f, indent=2)

def summarize_memory(user="naga"):
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        with open(MEMORY_PATH) as f:
            mem = json.load(f)
    except:
        return []
    today = datetime.date.today().isoformat()
    return [
        f"- {i['text']}"
        for i in mem.get(user, {}).get("facts", [])
        if i.get("date") == today
    ]
