# src/test_tts.py - Minimal VITS TTS implementation

import os
import sys
import sounddevice as sd
from TTS.api import TTS

# Get input file from command line arg or use default
input_file = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'

# Create example file if it doesn't exist
if not os.path.exists(input_file):
    with open(input_file, 'w') as f:
        f.write("Hello. I'm your voice assistant. How can I help you today?")
    print(f"Created {input_file} - edit it and run again")
    sys.exit(0)

# Read text from file
with open(input_file, 'r') as f:
    text = f.read().strip()

if not text:
    print("Input file is empty")
    sys.exit(1)

print(f"Synthesizing: {text[:50]}{'...' if len(text) > 50 else ''}")

# Suppress stdout/stderr during TTS operations
old_stdout, old_stderr = sys.stdout, sys.stderr
sys.stdout = sys.stderr = open(os.devnull, 'w')

try:
    # Load VITS model
    tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    
    # Recommended clear voices:
    # - Female: p225, p236, p261, p294, p266
    # - Male: p326, p270, p376, p330, p360
    
    # Use the p225 speaker (clear female voice)
    speaker = "p360"
    
    # Generate speech
    audio = tts.tts(text=text, speaker=speaker)
    
    # Restore stdout/stderr
    sys.stdout, sys.stderr = old_stdout, old_stderr
    print(f"Using voice: {speaker}")
    
    # Play audio
    sd.play(audio, samplerate=tts.synthesizer.output_sample_rate)
    sd.wait()
    print("Done")
    
except Exception as e:
    # Restore stdout/stderr before showing error
    sys.stdout, sys.stderr = old_stdout, old_stderr
    print(f"Error: {str(e)}")
    print("Install espeak-ng if missing: brew install espeak")
    sys.exit(1)

# Usage help
if __name__ == "__main__" and len(sys.argv) <= 1:
    print("\nUsage: python test_tts.py [input_file]")
    print("  input_file: Text file to read (default: input.txt)")
    print("\nExample: python test_tts.py my_text.txt")
