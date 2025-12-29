from gtts import gTTS
import os

text = "హాయ్! ఇది స్కార్లెట్ గొంతులో ఒక ప్రేమ కథ ప్రారంభం."
tts = gTTS(text, lang="te")
tts.save("/dev/shm/test_telugu.mp3")
os.system("mpg123 /dev/shm/test_telugu.mp3")

