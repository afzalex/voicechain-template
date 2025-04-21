import whisper
import numpy as np
import time
import os
import sys
import subprocess
import signal

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
        self.RECORD_DURATION = 5  # seconds (fixed recording duration)
        self.temp_file = "temp_recording.wav"
        
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
            self.record_audio(0.1)
            print("Audio setup successful!")
            
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
            duration (float, optional): Duration to record in seconds. If None, uses default duration.
        
        Returns:
            str: Path to the recorded audio file
        """
        if duration is None:
            duration = self.RECORD_DURATION
            
        try:
            print("Recording... Speak now!")
            
            # Use ffmpeg to record audio with minimal output
            command = [
                'ffmpeg',
                '-y',  # Overwrite output file if it exists
                '-f', 'avfoundation',  # Use avfoundation for macOS
                '-i', 'none:1',  # Use MacBook Air Microphone (index 1)
                '-t', str(duration),  # Duration in seconds
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
                '-ac', str(self.CHANNELS),  # Number of channels
                '-ar', str(self.RATE),  # Sample rate
                '-loglevel', 'error',  # Only show errors
                self.temp_file
            ]
            
            # Run ffmpeg command and suppress output
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return self.temp_file
            
        except subprocess.CalledProcessError as e:
            print(f"\nError recording audio: {e}")
            print("Please check your microphone permissions and connection.")
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
            # Record audio for a fixed duration
            audio_file = self.record_audio()
            if not audio_file:
                return None
            
            # Transcribe with Whisper
            result = self.model.transcribe(audio_file, language="en")
            text = result["text"].strip()
            
            # Clean up temporary file
            self._cleanup_temp_file()
            
            if text:
                print(f"You said: {text}")
                return text
            else:
                print("No speech detected")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            # Make sure to clean up even if there's an error
            self._cleanup_temp_file()
            return None
    
    def _cleanup_temp_file(self):
        """
        Clean up the temporary recording file.
        """
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")
    
    def __del__(self):
        """
        Cleanup when the object is destroyed.
        """
        self._cleanup_temp_file() 