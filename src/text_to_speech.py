import os
import tempfile
import subprocess
from gtts import gTTS

class TextToSpeech:
    def __init__(self, lang="en", slow=False):
        """
        Initialize the text-to-speech engine using Google Text-to-Speech.
        
        Args:
            lang (str): Language code (default: "en" for English)
            slow (bool): Whether to speak slowly (default: False for faster speech)
        """
        # Always use English for the conversation
        self.lang = "en"
        self.slow = slow  # False means faster speech
        
        # Test TTS setup
        try:
            self.speak("Hello! I'm ready to help.")
            print("TTS initialized successfully!")
        except Exception as e:
            print(f"\nERROR initializing TTS: {e}")
            print("Please check your internet connection.")
            raise e
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to convert to speech
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech using Google TTS (always in English)
            tts = gTTS(text=text, lang=self.lang, slow=self.slow)
            tts.save(temp_path)
            
            # Play the audio using ffplay with increased speed (1.5x)
            subprocess.run(['ffplay', '-nodisp', '-autoexit', '-af', 'atempo=1.5', temp_path], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"\nERROR in text-to-speech: {e}")
            print("Please check your internet connection.")
            raise e 