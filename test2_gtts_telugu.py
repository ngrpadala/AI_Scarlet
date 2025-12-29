from gtts import gTTS
import os

with open("/home/nagapi5/AI_code/code_copilot/v5_telugu/v5_v1/telugu_story1.txt", "r", encoding="utf-8") as f:
    text = f.read()

tts = gTTS(text, lang="te")
tts.save("/dev/shm/scarlet_telugu_poem.mp3")
os.system("mpg123 /dev/shm/scarlet_telugu_poem.mp3")

