"""Speech recognition component with WebRTC VAD and Whisper integration."""
import os
import numpy as np
import sounddevice as sd
import whisper
import struct
import platform
import webrtcvad
import logging
import time

# Get logger
logger = logging.getLogger("voice-assistant")

class SpeechRecognizer:
    """Speech recognition with voice activity detection using WebRTC VAD and Whisper."""

    def __init__(self, vad_mode=3, sample_rate=16000, whisper_model="tiny"):
        """Initialize the speech recognizer.
        
        Args:
            vad_mode: WebRTC VAD aggressiveness (0-3)
            sample_rate: Audio sample rate
            whisper_model: Whisper model size
        """
        self._temp_file = "temp_audio.wav"
        self._is_macos = platform.system() == 'Darwin'
        self._samplerate = sample_rate
        self._blocksize = 320  # 20ms at 16kHz
        self._channels = 1

        # Find the default input device
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:  # This is an input device
                    if 'MacBook Air Microphone' in dev['name']:
                        self._device = i
                        logger.info(f"🎤 Using input device: {dev['name']}")
                        break
            else:
                # If MacBook Air Microphone not found, use default input device
                self._device = sd.default.device[0]
                logger.info(f"🎤 Using default input device: {devices[self._device]['name']}")
        except Exception as e:
            logger.error(f"❌ Error finding audio device: {e}")
            self._device = None

        # Speech detection settings
        self._vad = webrtcvad.Vad(vad_mode)
        self._min_speech_frames = 3  # Reduced from 5 to 3 for faster detection
        
        # Continuous silence needed to end recording (in seconds)
        self._end_silence_sec = 2.0  # Reduced from 4.0 to 2.0 for faster response
        self._frames_per_second = self._samplerate / self._blocksize
        self._end_silence_frames = int(self._end_silence_sec * self._frames_per_second)
        
        # Maximum recording duration (in seconds)
        self._max_record_sec = 60.0
        self._max_frames = int(self._max_record_sec * self._frames_per_second)
        
        logger.debug("🔍 SpeechRecognizer initialized:")
        logger.debug(f"🔍 VAD mode: {vad_mode}, Sample rate: {sample_rate}")
        logger.debug(f"🔍 End silence: {self._end_silence_sec}s ({self._end_silence_frames} frames)")
        logger.debug(f"🔍 Max recording: {self._max_record_sec}s ({self._max_frames} frames)")

        # Load Whisper model
        logger.info(f"🎤 Loading Whisper model '{whisper_model}'...")
        try:
            self._whisper_model = whisper.load_model(whisper_model)
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading Whisper model: {e}")
            self._whisper_model = None

    def _is_loud_enough(self, block, threshold=0.01):  # Reduced from 0.02 to 0.01
        """Check if audio block is loud enough to be considered for speech detection."""
        return np.abs(block).mean() > threshold

    def _is_speech(self, block):
        """Use WebRTC VAD to check if block contains speech."""
        try:
            int16_block = np.int16(block.flatten() * 32767)
            pcm_bytes = struct.pack(f"{len(int16_block)}h", *int16_block)
            if len(pcm_bytes) < self._blocksize * 2:
                return False
            return self._vad.is_speech(pcm_bytes, sample_rate=self._samplerate)
        except Exception as e:
            logger.error(f"❌ VAD error: {e}")
            return False

    def listen(self):
        """Record audio until silence and transcribe it."""
        if self._device is None:
            logger.error("❌ No audio input device available")
            return None

        logger.info("🎙️ Listening... Speak now")
        
        audio_chunks = []      # All audio chunks
        consecutive_speech = 0 # Count of consecutive speech frames
        consecutive_silence = 0 # Count of consecutive silence frames
        is_recording = False    # Whether we've started recording speech
        total_frames = 0        # Total frames processed
        total_speech_frames = 0 # Total speech frames detected
        log_interval = 150      # How often to log status (in frames)
        
        try:
            with sd.InputStream(samplerate=self._samplerate,
                               channels=self._channels,
                               dtype='float32',
                               blocksize=self._blocksize,
                               device=self._device) as stream:
                logger.debug("✅ Audio stream opened successfully")
                
                try:
                    # Main recording loop
                    while total_frames < self._max_frames:
                        total_frames += 1
                        
                        # Read audio block
                        try:
                            block, _ = stream.read(self._blocksize)
                            audio_chunks.append(block.copy())
                        except Exception as e:
                            logger.error(f"❌ Error reading audio block: {e}")
                            continue
                        
                        # Detect speech in this block
                        is_speech_block = self._is_loud_enough(block) and self._is_speech(block)
                        
                        # Update speech/silence counters
                        if is_speech_block:
                            consecutive_speech += 1
                            consecutive_silence = 0
                            if is_recording:
                                total_speech_frames += 1
                        else:
                            consecutive_speech = 0
                            if is_recording:
                                consecutive_silence += 1
                        
                        # Start recording if we detect enough consecutive speech
                        if not is_recording and consecutive_speech >= self._min_speech_frames:
                            is_recording = True
                            consecutive_silence = 0
                            total_speech_frames = consecutive_speech
                            logger.info("🗣️ Speech detected")
                        
                        # Log status periodically
                        if total_frames % log_interval == 0:
                            if is_recording:
                                logger.debug(f"🔍 Recording: frame {total_frames}, speech frames: {total_speech_frames}, " +
                                            f"silence: {consecutive_silence}/{self._end_silence_frames}")
                            else:
                                logger.debug(f"🔍 Waiting: frame {total_frames}, consecutive speech: {consecutive_speech}/{self._min_speech_frames}")
                        
                        # Show countdown during silence
                        if is_recording and consecutive_silence > 0 and consecutive_silence % 50 == 0:
                            sec_remaining = (self._end_silence_frames - consecutive_silence) / self._frames_per_second
                            logger.debug(f"⏱️ Waiting for speech to resume... {sec_remaining:.1f}s remaining")
                        
                        # Stop if we have enough continuous silence after speech was detected
                        if is_recording and consecutive_silence >= self._end_silence_frames:
                            logger.info("⏹️ End of speech detected")
                            break
                    
                    # Handle maximum recording time
                    if total_frames >= self._max_frames:
                        logger.info("⏱️ Maximum recording time reached")
                
                except Exception as e:
                    logger.error(f"❌ Error during recording: {e}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Error opening audio stream: {e}")
            return None
        
        # Process recorded audio if we detected speech
        if is_recording and len(audio_chunks) > 0:
            audio_data = np.concatenate(audio_chunks, axis=0).flatten()
            audio_duration = len(audio_data) / self._samplerate
            logger.debug(f"🔍 Processing {audio_duration:.2f}s of audio with {total_speech_frames} speech frames")
            
            if self._whisper_model:
                try:
                    logger.info("🔄 Transcribing audio...")
                    result = self._whisper_model.transcribe(audio_data, language='en', fp16=False)
                    text = result['text'].strip()
                    if text:
                        logger.info(f"📝 Transcribed: \"{text}\"")
                        return text
                    else:
                        logger.info("❓ No speech content in recording")
                        return None
                except Exception as e:
                    logger.error(f"❌ Error transcribing speech: {e}")
                    return None
            else:
                logger.error("❌ Whisper model not available")
                return None
        else:
            logger.debug("⌛ No speech detected")
            return None
