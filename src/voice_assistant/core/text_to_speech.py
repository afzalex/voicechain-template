"""Text-to-speech component using gTTS for all platforms."""
import os
import platform
import subprocess
import time
import sys
import pygame
from gtts import gTTS
import logging

# Get logger
logger = logging.getLogger("voice-assistant")

class TextToSpeech:
    """Text-to-speech using Google Text-to-Speech (gTTS) for all platforms."""
    
    def __init__(self, lang="en", slow=False, rate=1.3):
        """Initialize text-to-speech engine.
        
        Args:
            lang (str): Language code (e.g., "en")
            slow (bool): Whether to speak slowly
            rate (float): Speech rate multiplier (higher is faster)
        """
        self._lang = lang
        self._slow = slow
        self._rate = rate  # Speech rate - higher is faster
        self._is_macos = platform.system() == 'Darwin'
        
        try:
            pygame.mixer.init()
            logger.info("Text-to-speech initialized successfully!")
        except Exception as e:
            logger.warning(f"Could not initialize pygame for audio playback: {e}")
        
    def speak(self, text):
        """Convert text to speech and play it using gTTS.
        
        Args:
            text (str): Text to speak
        """
        try:
            # Create temporary file
            temp_file = "temp_speech.mp3"
            
            # Generate speech with gTTS
            # Use slow=False for faster speech
            tts = gTTS(text=text, lang=self._lang, slow=False)
            tts.save(temp_file)
            
            # Play audio
            try:
                # Initialize pygame mixer
                pygame.mixer.init(frequency=24000)  # Higher frequency for better quality
                
                # Load and play the audio file
                pygame.mixer.music.load(temp_file)
                
                # Set playback speed using pygame's event handling
                # Unfortunately, pygame doesn't support direct speed control, so we use system tools if needed
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
            except Exception as e:
                # Fallback to system audio player if pygame fails
                logger.warning(f"Pygame playback failed: {e}, using system player")
                self._play_with_system(temp_file)
                
            # Cleanup
            os.remove(temp_file)
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    def _play_with_system(self, audio_file):
        """Fallback method to play audio using system tools with speed adjustment.
        
        Args:
            audio_file (str): Path to audio file
        """
        try:
            if sys.platform == "darwin":  # macOS
                # For macOS afplay, -r flag allows rate adjustment (1.0 is normal, 2.0 is double speed)
                # Using higher rate for faster speech
                subprocess.run(["afplay", "-r", str(self._rate), audio_file], check=True)
            elif sys.platform == "win32":  # Windows
                # Windows doesn't have a simple way to adjust playback speed via command line
                # So we just play the file normally
                os.startfile(audio_file)
                time.sleep(2)  # Give time for audio to play before cleanup
            else:  # Linux and others
                # Try using ffplay if available (part of ffmpeg) which supports speed adjustment
                try:
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", "-af", f"atempo={self._rate}", audio_file], 
                                  check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                except:
                    # Fallback to xdg-open if ffplay is not available
                    subprocess.run(["xdg-open", audio_file], check=True)
                    time.sleep(2)  # Give time for audio to play before cleanup
        except Exception as e:
            logger.error(f"Error playing audio with system tools: {e}")
            
    def __del__(self):
        """Clean up resources when object is destroyed."""
        try:
            pygame.mixer.quit()
        except:
            pass 