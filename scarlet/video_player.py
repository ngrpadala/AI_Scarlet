import os
import subprocess
import threading
import time
from pathlib import Path
from scarlet.config import VIDEO_DIR, INTIMACY_VIDEO_FOLDER, VIDEO_MAP

_video_process = None
_loop_thread = None
_loop_running = False

def play_once(expression):
    filename = VIDEO_MAP.get(expression, "")
    if not filename:
        print(f"[video_player] No video for: {expression}")
        return
    path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(path):
        print(f"[video_player] SKIP: path='{path}' exists=False")
        return
    subprocess.run([
        "/usr/bin/mpv", path,
        "--fs", "--no-border", "--geometry=0:0",
        "--vf=scale=800:480,setsar=0.75",
        "--really-quiet"
    ])

def start_loop(folder):
    global _loop_thread, _loop_running
    if not os.path.exists(folder):
        print(f"[video_player] LOOP folder not found: {folder}")
        return
    _loop_running = True
    _loop_thread = threading.Thread(target=_loop_videos_from_folder, args=(folder,), daemon=True)
    _loop_thread.start()

def _loop_videos_from_folder(folder):
    global _video_process
    while _loop_running:
        video_files = sorted([f for f in os.listdir(folder) if f.endswith(".mp4")])
        if not video_files:
            print(f"[video_player] No videos in {folder}")
            return
        for vid in video_files:
            if not _loop_running:
                break
            path = os.path.join(folder, vid)
            _video_process = subprocess.Popen([
                "/usr/bin/mpv", path,
                "--fs", "--no-border", "--geometry=0:0",
                "--loop=no", "--vf=scale=800:480,setsar=0.75",
                "--really-quiet"
            ])
            _video_process.wait()
            time.sleep(1)

def stop_loop():
    global _video_process, _loop_running
    _loop_running = False
    if _video_process and _video_process.poll() is None:
        _video_process.terminate()
        try:
            _video_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            _video_process.kill()
    _video_process = None

def start_intimacy_loop():
    # Loop all mp4s in intimacy folder
    if not os.path.exists(INTIMACY_VIDEO_FOLDER):
        print(f"[video_player] Intimacy folder not found: {INTIMACY_VIDEO_FOLDER}")
        return
    start_loop(INTIMACY_VIDEO_FOLDER)

def start_idle_loop():
    # Loop single idle.mp4 repeatedly
    idle_path = os.path.join(VIDEO_DIR, VIDEO_MAP.get("idle", "intimate_idle.mp4"))
    if not os.path.exists(idle_path):
        print(f"[video_player] Idle video not found at: {idle_path}")
        return
    start_loop_with_file(idle_path)

def start_loop_with_file(file_path):
    global _loop_thread, _loop_running
    _loop_running = True
    _loop_thread = threading.Thread(target=_loop_single_video, args=(file_path,), daemon=True)
    _loop_thread.start()

def _loop_single_video(path):
    global _video_process
    while _loop_running:
        _video_process = subprocess.Popen([
            "/usr/bin/mpv", path,
            "--fs", "--no-border", "--geometry=0:0",
            "--loop=no", "--vf=scale=800:480,setsar=0.75",
            "--really-quiet"
        ])
        _video_process.wait()

