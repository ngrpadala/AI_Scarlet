# wake_test.py

from pocketsphinx import LiveSpeech

# ✅ You can change the keyword and sensitivity here
WAKE_WORD = "scarlet"
SENSITIVITY = 1e-50  # Lower = more sensitive, try values like 1e-20, 1e-30, etc.

print(f"🎤 Listening for wake word: '{WAKE_WORD}' (sensitivity={SENSITIVITY})")

# Setup PocketSphinx live speech recognition
speech = LiveSpeech(
    lm=False,
    keyphrase=WAKE_WORD,
    kws_threshold=SENSITIVITY,
    verbose=False
)

# Loop to listen continuously
for phrase in speech:
    print(f"✅ Detected wake word: '{WAKE_WORD}'")

