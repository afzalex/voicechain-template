import os
import re
import webrtcvad
import numpy as np
import sounddevice as sd
import whisper
import struct
import platform
import pygame
import subprocess
import time
import sys
from gtts import gTTS
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import logging

# Ensure environment variables are loaded
load_dotenv()

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("voice-assistant")

class SpeechRecognizer:
    def __init__(self, vad_mode=3, sample_rate=16000, whisper_model="tiny"):
        """Initialize speech recognizer with WebRTC VAD and Whisper"""
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
        if os.path.exists(self._temp_file):
            try:
                os.remove(self._temp_file)
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {e}")
                
    def __del__(self):
        self._cleanup_temp_file()
    
    def _is_loud_enough(self, block, threshold=0.05):
        """Check if the audio block is loud enough to be real speech"""
        return np.abs(block).mean() > threshold
    
    def _is_speech(self, block):
        """Check if VAD thinks the user is speaking"""
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
        """Record audio until silence and transcribe it"""
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

class TextToSpeech:
    def __init__(self, lang="en", slow=False, rate=1.1):
        self._lang = lang
        self._slow = slow
        self._rate = rate  # Speech rate - higher is faster
        self._is_macos = platform.system() == 'Darwin'
        
        # On macOS, we'll prioritize the system's 'say' command
        if not self._is_macos:
            try:
                pygame.mixer.init()
                logger.info("Text-to-speech initialized successfully!")
            except Exception as e:
                logger.warning(f"Could not initialize pygame for audio playback: {e}")
        else:
            logger.info("Using macOS native text-to-speech")
        
    def speak(self, text):
        # For macOS, use the built-in 'say' command which works reliably
        if self._is_macos:
            try:
                # Use the -r parameter to control rate (words per minute)
                # Default is around 175-180, using a slightly faster rate of 190
                subprocess.run(["say", "-r", "190", text], check=True)
                return
            except Exception as e:
                logger.error(f"Error using macOS text-to-speech: {e}, falling back to gTTS")
                # Fall back to gTTS if 'say' fails
        
        try:
            # Create temporary file
            temp_file = "temp_speech.mp3"
            
            # Generate speech - gTTS doesn't have direct speed control, only slow=True/False
            # So we'll use slow=False for normal speed
            tts = gTTS(text=text, lang=self._lang, slow=False)
            tts.save(temp_file)
            
            # Play audio at normal speed
            try:
                pygame.mixer.init(frequency=22050)  # Standard frequency
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except Exception as e:
                # Fallback to system audio player if pygame fails
                self._play_with_system(temp_file)
                
            # Cleanup
            os.remove(temp_file)
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    def _play_with_system(self, audio_file):
        """Fallback method to play audio using system tools"""
        try:
            if sys.platform == "darwin":  # macOS
                # For macOS afplay, -r flag allows rate adjustment (1.0 is normal, 2.0 is double speed)
                subprocess.run(["afplay", "-r", "1.1", audio_file], check=True)
            elif sys.platform == "win32":  # Windows
                os.startfile(audio_file)
                time.sleep(2)  # Give time for audio to play before cleanup
            else:  # Linux and others
                subprocess.run(["xdg-open", audio_file], check=True)
                time.sleep(2)  # Give time for audio to play before cleanup
        except Exception as e:
            logger.error(f"Error playing audio with system tools: {e}")
            
    def __del__(self):
        if not self._is_macos:
            try:
                pygame.mixer.quit()
            except:
                pass

class VoiceAgent:
    def __init__(self):
        # Initialize components
        self.speech_recognizer = SpeechRecognizer(vad_mode=3, whisper_model="base")
        self.text_to_speech = TextToSpeech()
        
        # Available actions
        self.actions = {
            "cancel_appointment": self._cancel_appointment,
            "exit": self._exit_conversation
        }
        
        # Initialize LangChain components
        try:
            self._init_langchain()
            logger.info("Voice Agent initialized!")
        except Exception as e:
            logger.error(f"Error initializing Voice Agent: {e}")
            raise
    
    def _init_langchain(self):
        # Initialize Ollama LLM
        try:
            # Try to get the host from environment variable
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            self.llm = Ollama(model="llama3", base_url=ollama_host)
            
            # Setup conversation memory
            self.memory = ConversationBufferMemory()
            
            # Setup prompt template
            template = """
            You are a helpful AI assistant. You provide concise, helpful answers to questions.
            
            Current conversation:
            {history}
            Human: {input}
            AI:"""
            
            self.prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )

            # Setup intent detection prompt
            self.intent_prompt = PromptTemplate(
                input_variables=["input"],
                template="""
                Your task is to determine if this user request requires a specific action.
                
                Available actions:
                - cancel_appointment: When the user wants to cancel an appointment, meeting, or reservation
                - exit: When the user wants to end the conversation, say goodbye, or quit
                - none: When no specific action is required, just respond normally
                
                User request: {input}
                
                Return only the action name without explanation. For example: "cancel_appointment", "exit", or "none".
                Action:"""
            )
            
            # Setup conversation chain with warning suppression
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                self.conversation = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    prompt=self.prompt,
                    verbose=False
                )
        except Exception as e:
            logger.error(f"Error connecting to Ollama at {ollama_host}: {e}")
            logger.error("Make sure Ollama is running with: ollama serve")
            logger.error("And ensure llama3 model is available with: ollama pull llama3")
            raise
    
    def _detect_intent(self, text):
        """Use the LLM to detect the intent of the user's request"""
        try:
            response = self.llm.invoke(self.intent_prompt.format(input=text)).strip().lower()
            logger.debug(f"Intent detected: '{response}'")
            
            # Validate the response
            if response in self.actions or response == "none":
                return response
            else:
                logger.warning(f"Invalid intent detected: '{response}', defaulting to 'none'")
                return "none"
                
        except Exception as e:
            logger.error(f"Error in intent detection: {e}")
            return "none"
    
    def _cancel_appointment(self, text):
        """Dummy function to simulate appointment cancellation"""
        logger.info("🗑️ DUMMY FUNCTION: Would have cancelled appointment here")
        # In a real implementation, this would connect to a calendar service
        # or database to actually cancel the appointment
        return "I've cancelled your appointment. You will receive a confirmation email shortly."
    
    def _exit_conversation(self, text):
        """Handle exit command"""
        logger.info("👋 User has requested to exit the conversation")
        return "exit_signal"  # Special return value to signal exit
    
    def listen(self):
        """Listen for user input through voice"""
        return self.speech_recognizer.listen()
    
    def speak(self, text):
        """Speak the response"""
        self.text_to_speech.speak(text)
    
    def process(self, text):
        """Process user input and generate a response"""
        if not text:
            return "I didn't catch that. Could you please repeat?"
        
        # First, detect the intent
        intent = self._detect_intent(text)
        
        # If an action is required, execute it
        if intent in self.actions:
            logger.info(f"Executing action: {intent}")
            return self.actions[intent](text)
            
        # Otherwise, use the conversation chain for normal responses
        try:
            response = self.conversation.predict(input=text)
            return response
        except Exception as e:
            logger.error(f"Error processing with LangChain: {e}")
            return "I'm having trouble processing your request."
    
    def run(self):
        """Run the assistant in a loop"""
        logger.info("="*50)
        logger.info("Voice Assistant is ready!")
        logger.info("Simply speak to interact with the assistant")
        logger.info("Say 'exit', 'quit', or 'goodbye' to end the session")
        logger.info("="*50)
        
        self.speak("Voice assistant is ready. You can speak to me now.")
        
        while True:
            try:
                # Listen for speech input
                user_input = self.listen()
                
                if user_input:
                    # Process and respond
                    logger.info("Processing...")
                    response = self.process(user_input)
                    
                    # Check for exit signal
                    if response == "exit_signal":
                        logger.info("Goodbye!")
                        self.speak("Goodbye!")
                        break
                        
                    logger.info(f"Assistant: {response}")
                    self.speak(response)
                
            except KeyboardInterrupt:
                logger.info("Goodbye!")
                self.speak("Goodbye!")
                break
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                continue 