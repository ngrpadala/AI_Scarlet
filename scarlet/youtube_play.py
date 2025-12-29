import subprocess
import os

def play_youtube_video(youtube_url):
    output_path = "/dev/shm/video.mp4"

    try:
        subprocess.run([
            "yt-dlp", "-f", "mp4", "-o", output_path, youtube_url
        ], check=True)

        subprocess.run(["mpv", output_path])

        if os.path.exists(output_path):
            os.remove(output_path)

        return "Video played successfully."
    except subprocess.CalledProcessError as e:
        return f"Download/playback failed: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

