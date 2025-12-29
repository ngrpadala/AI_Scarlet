import os
from time import sleep

story_file = "/home/nagapi5/AI_code/code_copilot/v5_telugu/v5_v1/fantasy_story_en.txt"
model_path = "/home/nagapi5/piper_voices/en/en_GB-jenny_dioco-medium.onnx"

output_wav = "/dev/shm/fantasy_out.wav"

with open(story_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue
    print(f"Speaking line {idx+1}: {line[:60]}...")
    temp_out = f"/dev/shm/line_{idx}.wav"
    cmd = f'echo "{line}" | piper --model {model_path} --output_file {temp_out}'
    os.system(cmd)
    os.system(f"aplay {temp_out}")
    sleep(0.3)

