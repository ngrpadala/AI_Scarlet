#!/usr/bin/env python3
import subprocess
import time
import os

# Point this at a file you know exists and plays in mpv.
VIDEO = "/home/nagapi5/scarlet/videos/idle.mp4"

if not os.path.isfile(VIDEO):
    print(f"ERROR: video not found at {VIDEO}")
    exit(1)

# Show exactly what we’ll run
cmd = ["mpv", VIDEO]
print("Running command:", cmd)

# Launch mpv
proc = subprocess.Popen(cmd)

# If you like, wait a bit so the script doesn't exit immediately
time.sleep(5)
