from gtts import gTTS
import os

#text = "హలో, మీరు సరేనా?"
text = "మీరు ఈరోజు ఎలా ఉన్నారు?"
tts = gTTS(text, lang="te")
tts.save("/dev/shm/test_telugu.mp3")
os.system("mpg123 /dev/shm/test_telugu.mp3")

