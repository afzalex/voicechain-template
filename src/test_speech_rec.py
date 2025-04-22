# src/test.py

import re
import webrtcvad
import numpy as np
import sounddevice as sd
import whisper
import struct
import logging

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("voice-assistant")

# Init Whisper and VAD
model = whisper.load_model("base")
vad = webrtcvad.Vad(3)  # Max aggressiveness

# Audio parameters
samplerate = 16000
blocksize = 320  # 20ms at 16kHz
channels = 1
silence_limit = 30  # ~6 seconds
required_speaking_frames = 5
reset_silence_on_new_speech = 3  # reset silence counter if speech resumes quickly

# Check if block is loud enough to be real speech
def is_loud_enough(block, threshold=0.01):
    return np.abs(block).mean() > threshold

# Check if VAD thinks user is speaking
def is_speech(block):
    int16_block = np.int16(block.flatten() * 32767)
    pcm_bytes = struct.pack(f"{len(int16_block)}h", *int16_block)
    if len(pcm_bytes) < blocksize * 2:
        return False
    return vad.is_speech(pcm_bytes, sample_rate=samplerate)

def is_exit_command(text):
    return re.fullmatch(r"\s*exit\s*\.?\s*", text, re.IGNORECASE) is not None

def record_until_silence():
    logger.info("🎙️ Listening... Speak now.")
    audio_chunks = []
    silence_count = 0
    speaking = False
    speaking_frames = 0

    with sd.InputStream(samplerate=samplerate, channels=channels, dtype='float32', blocksize=blocksize) as stream:
        while True:
            block, _ = stream.read(blocksize)
            audio_chunks.append(block.copy())

            if is_loud_enough(block) and is_speech(block):
                speaking_frames += 1
                if speaking:
                    silence_count = max(0, silence_count - reset_silence_on_new_speech)
                if speaking_frames >= required_speaking_frames and not speaking:
                    speaking = True
                    silence_count = 0
                    logger.info("✅ Speech started")
            elif speaking:
                silence_count += 1

            if speaking and silence_count > silence_limit:
                logger.info("🛑 Speech ended")
                break

    audio_data = np.concatenate(audio_chunks, axis=0).flatten()
    return audio_data

while True:
    try:
        audio = record_until_silence()
        logger.info("🔊 Transcribing...")
        result = model.transcribe(audio, language='en', fp16=False)
        text = result['text'].strip()
        logger.info("📝 " + text if text else "📝 (no speech detected)")
        if is_exit_command(text):
            logger.info("🛑 Exiting.")
            break
    except KeyboardInterrupt:
        logger.info("🛑 Exiting.")
        break

