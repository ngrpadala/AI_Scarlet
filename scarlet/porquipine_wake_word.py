# scarlet/wake_word.py

import os
import pyaudio
from pvporcupine import create
from scarlet.config import ACCESS_KEY_PATH, WAKE_WORD_FILE

porcupine = None
_pa = None
_stream = None

def init_porcupine():
    global porcupine, _pa, _stream
    if porcupine:
        return  # already initialized
    access_key = open(ACCESS_KEY_PATH).read().strip()
    porcupine = create(access_key=access_key, keyword_paths=[WAKE_WORD_FILE])
    _pa = pyaudio.PyAudio()
    _stream = _pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

def stop_porcupine():
    global porcupine, _stream, _pa
    if _stream:
        _stream.stop_stream()
        _stream.close()
        _stream = None
    if porcupine:
        porcupine.delete()
        porcupine = None
    if _pa:
        _pa.terminate()
        _pa = None

def detect():
    global porcupine, _stream
    if not porcupine or not _stream:
        init_porcupine()
    pcm = _stream.read(porcupine.frame_length, exception_on_overflow=False)
    pcm = [int.from_bytes(pcm[i:i+2], 'little', signed=True) for i in range(0, len(pcm), 2)]
    result = porcupine.process(pcm)
    return result >= 0

