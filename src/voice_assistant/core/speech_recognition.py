"""Speech recognition component with WebRTC VAD and Whisper integration."""
import os
import numpy as np
import sounddevice as sd
import whisper
import struct
import platform
import webrtcvad
import logging

# Get logger
logger = logging.getLogger("voice-assistant")

class SpeechRecognizer:
    """Speech recognition with voice activity detection using WebRTC VAD and Whisper."""
    
    def __init__(self, vad_mode=3, sample_rate=16000, whisper_model="tiny"):
        """Initialize speech recognizer with WebRTC VAD and Whisper.
        
        Args:
            vad_mode (int): WebRTC VAD aggressiveness (0-3)
            sample_rate (int): Audio sample rate
            whisper_model (str): Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self._temp_file = "temp_audio.wav"
        self._is_macos = platform.system() == 'Darwin'
        self._samplerate = sample_rate
        self._blocksize = 320  # 20ms at 16kHz
        self._channels = 1
        
        # WebRTC VAD settings
        self._vad = webrtcvad.Vad(vad_mode)
        self._silence_limit = 30  # ~6 seconds
        self._required_speaking_frames = 5
        self._reset_silence_on_new_speech = 3
        
        # Load Whisper model for speech recognition
        logger.info(f"Loading Whisper model '{whisper_model}'...")
        try:
            self._whisper_model = whisper.load_model(whisper_model)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            logger.error("Voice recognition will not be available")
            self._whisper_model = None
    
    def _cleanup_temp_file(self):
        """Remove temporary audio file if it exists."""
        if os.path.exists(self._temp_file):
            try:
                os.remove(self._temp_file)
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {e}")
                
    def __del__(self):
        """Clean up resources when object is destroyed."""
        self._cleanup_temp_file()
    
    def _is_loud_enough(self, block, threshold=0.05):
        """Check if the audio block is loud enough to be real speech.
        
        Args:
            block (numpy.ndarray): Audio block data
            threshold (float): Volume threshold
            
        Returns:
            bool: True if the audio is loud enough
        """
        return np.abs(block).mean() > threshold
    
    def _is_speech(self, block):
        """Check if VAD thinks the user is speaking.
        
        Args:
            block (numpy.ndarray): Audio block data
            
        Returns:
            bool: True if speech is detected
        """
        try:
            int16_block = np.int16(block.flatten() * 32767)
            pcm_bytes = struct.pack(f"{len(int16_block)}h", *int16_block)
            if len(pcm_bytes) < self._blocksize * 2:
                return False
            return self._vad.is_speech(pcm_bytes, sample_rate=self._samplerate)
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def listen(self):
        """Record audio until silence and transcribe it.
        
        Returns:
            str or None: Transcribed text or None if no speech detected
        """
        logger.info("🎙️ Listening... Speak now.")
        audio_chunks = []
        silence_count = 0
        speaking = False
        speaking_frames = 0

        with sd.InputStream(samplerate=self._samplerate, 
                           channels=self._channels, 
                           dtype='float32', 
                           blocksize=self._blocksize) as stream:
            try:
                while True:
                    block, _ = stream.read(self._blocksize)
                    audio_chunks.append(block.copy())

                    if self._is_loud_enough(block) and self._is_speech(block):
                        speaking_frames += 1
                        if speaking:
                            silence_count = max(0, silence_count - self._reset_silence_on_new_speech)
                        if speaking_frames >= self._required_speaking_frames and not speaking:
                            speaking = True
                            silence_count = 0
                            logger.info("✅ Speech started")
                    elif speaking:
                        silence_count += 1

                    if speaking and silence_count > self._silence_limit:
                        logger.info("🛑 Speech ended")
                        break
            except Exception as e:
                logger.error(f"Error recording audio: {e}")
                return None

        # Process the recorded audio
        if len(audio_chunks) > 0 and speaking:
            audio_data = np.concatenate(audio_chunks, axis=0).flatten()
            # Transcribe with Whisper
            if self._whisper_model:
                try:
                    logger.info("🔊 Transcribing...")
                    result = self._whisper_model.transcribe(audio_data, language='en', fp16=False)
                    text = result['text'].strip()
                    if text:
                        logger.info(f"📝 You said: {text}")
                        return text
                    else:
                        logger.info("📝 No speech detected")
                except Exception as e:
                    logger.error(f"Error transcribing speech: {e}")
        
        return None 