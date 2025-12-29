# test_laugh_natural.py
import random, time
from scarlet.tts import speak

def rand(a,b): return round(random.uniform(a,b), 2)

def make_laugh_ssml(style="giggle"):
    # tiny random variations each run
    r1, r2, r3 = rand(0.96,1.10), rand(0.92,1.06), rand(0.98,1.12)
    p1, p2, p3 = f"+{random.randint(1,5)}st", f"+{random.randint(0,4)}st", f"+{random.randint(2,6)}st"
    b1, b2, b3 = f"{random.randint(70,140)}ms", f"{random.randint(60,130)}ms", f"{random.randint(80,160)}ms"

    if style == "giggle":
        seq = ["he", "he", "hehe", "hehe", "he", "he"]
    elif style == "chuckle":
        seq = ["ha", "ha", "haha", "ha", "hah"]
    else:
        seq = ["ha", "ha", "haha", "hehe"]

    parts = []
    for i, syl in enumerate(seq):
        rate = [r1,r2,r3][i % 3]
        pitch = [p1,p2,p3][i % 3]
        parts.append(f"<prosody rate='{rate}' pitch='{pitch}' volume='loud'>{syl}</prosody>")
        if i != len(seq)-1:
            parts.append(f"<break time='{[b1,b2,b3][i % 3]}'/>")

    # add a breathy fade at the end
    parts.append("<break time='120ms'/>")
    parts.append("<prosody rate='0.92' pitch='-1st' volume='x-soft'>huh</prosody>")

    return "<speak>" + "".join(parts) + "</speak>"

if __name__ == "__main__":
    styles = ["giggle","chuckle","giggle","chuckle"]
    style = random.choice(styles)
    print(f"[Scarlet says]: (laughs: {style})")
    ssml = make_laugh_ssml(style)
    speak(ssml)  # your speak() should treat <speak> as SSML
    time.sleep(0.2)

