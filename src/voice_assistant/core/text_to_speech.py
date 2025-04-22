"""Text-to-speech component using Coqui TTS VITS."""
import os
import sys
import time
import sounddevice as sd
from TTS.api import TTS
import logging

# Get logger
logger = logging.getLogger("voice-assistant")

class TextToSpeech:
    """Text-to-speech using Coqui TTS VITS for natural-sounding voices."""
    
    def __init__(self, model_name="tts_models/en/vctk/vits", speaker="p360"):
        """Initialize text-to-speech engine.
        
        Args:
            model_name (str): Model name for TTS
            speaker (str): Speaker voice ID
                - Female options: p225, p236, p261, p294, p266
                - Male options: p326, p270, p376, p330, p360
        """
        self._model_name = model_name
        self._speaker = speaker
        self._tts = None
        self._sample_rate = 22050  # Default, will be updated after model loads
        
        logger.info("🔊 Initializing text-to-speech system...")
        logger.info(f"🔊 Loading voice model: {model_name}")
        logger.info(f"🔊 Using speaker voice: {speaker}")
        
        # Load the TTS model (this blocks but provides immediate feedback)
        self._load_model()
    
    def _load_model(self):
        """Load the TTS model with status updates."""
        try:
            # Suppress stdout/stderr during TTS operations to avoid verbose output
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = open(os.devnull, 'w')
            
            # Load the model
            start_time = time.time()
            self._tts = TTS(model_name=self._model_name, progress_bar=False, gpu=False)
            load_time = time.time() - start_time
            
            # Restore stdout/stderr
            sys.stdout, sys.stderr = old_stdout, old_stderr
            
            # Update sample rate from loaded model
            self._sample_rate = self._tts.synthesizer.output_sample_rate
            
            logger.info(f"✅ Voice model loaded successfully in {load_time:.1f} seconds")
            
        except Exception as e:
            # Restore stdout/stderr before showing error
            if 'old_stdout' in locals() and 'old_stderr' in locals():
                sys.stdout, sys.stderr = old_stdout, old_stderr
                
            logger.error(f"❌ Error loading TTS model: {str(e)}")
            if "espeak" in str(e).lower():
                logger.error("⚠️ Missing espeak dependency. Install with: brew install espeak")
            
            logger.error(f"Failed to initialize TTS: {e}")
            # Don't raise the exception - we'll handle failures in speak()
    
    def speak(self, text):
        """Convert text to speech and play it.
        
        Args:
            text (str): Text to speak
        """
        # Note: No longer printing text here since agent.py handles that
        
        if not self._tts:
            logger.warning("TTS model not initialized, using text-only output")
            return
            
        try:
            # Suppress stdout/stderr during generation
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = open(os.devnull, 'w')
            
            # Generate speech
            audio = self._tts.tts(text=text, speaker=self._speaker)
            
            # Restore stdout/stderr
            sys.stdout, sys.stderr = old_stdout, old_stderr
            
            # Play audio
            sd.play(audio, samplerate=self._sample_rate)
            sd.wait()  # Wait until audio is finished playing
            
        except Exception as e:
            # Restore stdout/stderr in case of error
            if 'old_stdout' in locals() and 'old_stderr' in locals():
                sys.stdout, sys.stderr = old_stdout, old_stderr
                
            logger.error(f"❌ Error in text-to-speech: {str(e)}")
    
    def __del__(self):
        """Clean up resources when object is destroyed."""
        try:
            # Nothing specific to clean up for our TTS implementation
            pass
        except Exception:
            pass 