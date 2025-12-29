#!/usr/bin/env python3
import subprocess
import sys
import glob
import os

"""
Usage:
  # 1) Play a local file:
  ./test_video_play.py /full/path/to/your/video.mp4

  # 2) Download & play a YouTube URL:
  ./test_video_play.py https://www.youtube.com/watch?v=9q8kkmCa9GY
"""

def download_youtube(url: str) -> str:
    outtmpl = "/tmp/ytvideo.%(ext)s"
    cmd = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio",
        "-o", outtmpl,
        url
    ]
    print("Downloading with yt-dlp:", cmd)
    subprocess.check_call(cmd)

    files = glob.glob("/tmp/ytvideo.*")
    if not files:
        raise FileNotFoundError("No downloaded file in /tmp/")
    files.sort(key=os.path.getmtime)
    return files[-1]

def play_path(path: str):
    cmd = ["mpv", path]
    print("Launching mpv:", cmd)
    subprocess.Popen(cmd)

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    if target.startswith("http"):
        video_file = download_youtube(target)
    else:
        video_file = target
        if not os.path.isfile(video_file):
            print("Error: file not found", video_file)
            sys.exit(1)

    play_path(video_file)

if __name__ == "__main__":
    main()
