import torch

# ✅ Limit CPU threads (optional but useful on Pi5 or low-resource systems)
torch.set_num_threads(1)

# ✅ Load the VAD model and utilities from Torch Hub
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=True  # Change to False after first time
)

# ✅ Get the helper functions
(get_speech_timestamps, _, read_audio, _, _) = utils

# ✅ Read and analyze audio file
wav = read_audio("/dev/shm/test.wav", sampling_rate=16000)
timestamps = get_speech_timestamps(wav, model, sampling_rate=16000, return_seconds=True)

# ✅ Print detected speech segments
if timestamps:
    print("✅ Speech detected at:", timestamps)
else:
    print("❌ No speech detected.")

