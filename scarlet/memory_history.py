# scarlet/memory_history.py
import os, json, time, threading
from typing import List, Dict, Any, Optional

HIST_DIR = "/home/nagapi5/scarlet/history"
MAX_FILE_SIZE_MB = 200
ROTATE_KEEP = 3
CONTEXT_MAX_TURNS = 40
CONTEXT_MAX_CHARS = 24000

_lock = threading.Lock()
os.makedirs(HIST_DIR, exist_ok=True)

def _user_path(user: str) -> str:
    safe = "".join(c for c in (user or "guest").lower() if c.isalnum() or c in ("_", "-"))
    return os.path.join(HIST_DIR, f"{safe}.jsonl")

def _rotate_if_needed(path: str):
    try:
        sz = os.path.getsize(path)
    except FileNotFoundError:
        return
    if sz < MAX_FILE_SIZE_MB * 1024 * 1024:
        return
    ts = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    os.replace(path, f"{path}.{ts}")
    base = os.path.basename(path)
    rotates = sorted([p for p in os.listdir(HIST_DIR) if p.startswith(base + ".")])
    for name in rotates[:-ROTATE_KEEP]:
        try: os.remove(os.path.join(HIST_DIR, name))
        except FileNotFoundError: pass

def append_turn(user: str, role: str, text: str, meta: Optional[Dict[str, Any]] = None):
    rec = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S%z", time.localtime()),
        "role": role, "text": text, "meta": meta or {}
    }
    line = json.dumps(rec, ensure_ascii=False)
    path = _user_path(user)
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        _rotate_if_needed(path)

def load_all(user: str) -> List[Dict[str, Any]]:
    path = _user_path(user); out=[]
    try:
        with open(path, "r", encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    try: out.append(json.loads(ln))
                    except Exception: continue
    except FileNotFoundError:
        pass
    return out

def get_context_for_llm(user: str) -> List[Dict[str, str]]:
    history = load_all(user)
    msgs = [{"role": r["role"], "content": r["text"]} for r in history]
    msgs = msgs[-CONTEXT_MAX_TURNS:]
    total = 0; trimmed=[]
    for m in reversed(msgs):
        ln = len(m["content"])
        if total + ln > CONTEXT_MAX_CHARS and trimmed:
            break
        trimmed.append(m); total += ln
    trimmed.reverse()
    return trimmed

def nuke_user_history(user: str):
    path = _user_path(user)
    with _lock:
        for name in [path] + [os.path.join(HIST_DIR, n) for n in os.listdir(HIST_DIR) if n.startswith(os.path.basename(path) + ".")]:
            try: os.remove(name)
            except FileNotFoundError: pass

