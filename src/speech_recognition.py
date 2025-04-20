import whisper
import numpy as np
import time
import os
import sys
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import subprocess

class SpeechRecognizer:
    def __init__(self, model_size="base"):
        """
        Initialize the speech recognizer with Whisper.
        
        Args:
            model_size (str): Size of the Whisper model to use. Options: "tiny", "base", "small", "medium", "large"
        """
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        
        # Audio recording parameters
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 10
        
        try:
            # Test the audio setup immediately
            self.test_audio_setup()
            
        except Exception as e:
            print("\nError initializing audio:")
            print(str(e))
            if "PermissionError" in str(e):
                print("\nMicrophone permission is required. Please follow these steps:")
                print("1. Open System Preferences/Settings")
                print("2. Go to Security & Privacy/Privacy")
                print("3. Select 'Microphone' from the left sidebar")
                print("4. Make sure your Terminal/IDE is checked in the list")
                print("5. Restart your Terminal/IDE after granting permissions")
                sys.exit(1)
            raise e

    def test_audio_setup(self):
        """Test the audio setup to catch permission issues early."""
        try:
            # Test recording for a very short duration
            self.record_audio(duration=0.1)
            print("\nAudio setup successful!")
            
        except Exception as e:
            if "PermissionError" in str(e):
                print("\nMicrophone permission is required. Please follow these steps:")
                print("1. Open System Preferences/Settings")
                print("2. Go to Security & Privacy/Privacy")
                print("3. Select 'Microphone' from the left sidebar")
                print("4. Make sure your Terminal/IDE is checked in the list")
                print("5. Restart your Terminal/IDE after granting permissions")
                sys.exit(1)
            raise e

    def record_audio(self, duration=None):
        """
        Record audio from microphone using ffmpeg.
        
        Args:
            duration (float, optional): Duration to record in seconds. Defaults to self.RECORD_SECONDS.
        
        Returns:
            str: Path to the recorded audio file
        """
        try:
            if duration is None:
                duration = self.RECORD_SECONDS
                
            print("\nPreparing to record...")
            print("Recording... Speak now!")
            
            # Create temporary file path
            temp_file = "temp_recording.wav"
            
            # Use ffmpeg to record audio
            command = [
                'ffmpeg',
                '-y',  # Overwrite output file if it exists
                '-f', 'avfoundation',  # Use avfoundation for macOS
                '-i', ':0',  # Use default input device
                '-t', str(duration),  # Duration in seconds
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
                '-ac', str(self.CHANNELS),  # Number of channels
                '-ar', str(self.RATE),  # Sample rate
                temp_file
            ]
            
            # Run ffmpeg command
            subprocess.run(command, check=True, capture_output=True)
            
            print("Recording finished.")
            return temp_file
            
        except subprocess.CalledProcessError as e:
            print(f"\nError recording audio: {e}")
            print("Please check your microphone permissions and connection.")
            if e.stderr:
                print(f"Error details: {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"\nError recording audio: {e}")
            print("Please check your microphone permissions and connection.")
            return None
    
    def listen(self):
        """
        Listen for speech and convert it to text using Whisper.
        
        Returns:
            str: Recognized text or None if recognition fails
        """
        try:
            # Record audio
            audio_file = self.record_audio()
            if not audio_file:
                return None
            
            print("Processing speech with Whisper...")
            # Transcribe with Whisper
            result = self.model.transcribe(audio_file)
            text = result["text"].strip()
            
            # Clean up temporary file
            os.remove(audio_file)
            
            if text:
                print(f"Recognized: {text}")
                return text
            else:
                print("No speech detected")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def __del__(self):
        """
        Cleanup when the object is destroyed.
        """
        if self.audio:
            self.audio.terminate() 