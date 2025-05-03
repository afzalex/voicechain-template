"""Main Voice Assistant Agent that coordinates speech, TTS, and other components."""
import logging
from typing import Optional, Dict, Callable

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaLLM

from ..config import AssistantConfig, load_config
from ..interfaces import (
    SpeechRecognizerInterface,
    TextToSpeechInterface,
    LLMInterface,
    ActionHandlerInterface
)
from ..prompts.prompts import PromptTemplates
from .speech_recognition import SpeechRecognizer
from .text_to_speech import TextToSpeech
from .appointment_actions import AppointmentActions
from ..utils.date_utils import normalize_date

# Get logger
logger = logging.getLogger("voice-assistant")

class VoiceAgent:
    """Main voice assistant agent that coordinates speech recognition and text-to-speech."""
    
    def __init__(self, config: Optional[AssistantConfig] = None):
        """Initialize the voice agent with required components.
        
        Args:
            config (Optional[AssistantConfig]): Configuration object. If None, loads from environment.
        """
        logger.debug("Initializing VoiceAgent...")
        
        self.config = config or load_config()
        logger.debug("Configuration loaded")
        logger.debug(f"Config: {self.config}")
        
        logger.debug("Loading prompt templates...")
        self.prompts = PromptTemplates()
        logger.debug("Prompt templates loaded")
        
        logger.info("="*60)
        logger.info("📱 VOICE ASSISTANT INITIALIZATION")
        logger.info("="*60)
        
        # Initialize components
        logger.debug("Initializing components...")
        self._init_components()
        logger.debug("Components initialized")
        
        # Setup conversation chain
        logger.debug("Setting up conversation chain...")
        self._setup_conversation_chain()
        logger.debug("Conversation chain setup complete")
        
        logger.info("✅ Voice Assistant fully initialized!")
    
    def _init_components(self):
        """Initialize all required components."""
        logger.debug("Initializing text-to-speech...")
        # Initialize text-to-speech first for better UX
        self.text_to_speech = TextToSpeech(
            model_name=self.config.tts.model_name,
            speaker=self.config.tts.speaker
        )
        logger.debug("Text-to-speech initialized")
        
        # Initialize speech recognition
        logger.info("🎤 Initializing speech recognition...")
        self.speech_recognizer = SpeechRecognizer(
            vad_mode=self.config.speech.vad_mode,
            sample_rate=self.config.speech.sample_rate,
            whisper_model=self.config.speech.whisper_model
        )
        logger.debug("Speech recognition initialized")
        
        # Initialize LLM
        logger.info("🧠 Initializing language model...")
        self.llm = OllamaLLM(
            model=self.config.llm.model,
            base_url=self.config.llm.base_url
        )
        logger.debug("Language model initialized")
        
        # Initialize appointment actions
        logger.debug("Initializing appointment actions...")
        self.appointment_actions = AppointmentActions(self.llm)
        logger.debug("Appointment actions initialized")
        
        # Setup available actions
        logger.debug("Setting up available actions...")
        self.actions: Dict[str, Callable] = {
            "cancel_appointment": self._cancel_appointment,
            "schedule_appointment": self._schedule_appointment,
            "exit": self._exit_conversation
        }
        logger.debug("Actions setup complete")
    
    def _setup_conversation_chain(self):
        """Setup the conversation chain with LangChain."""
        # Setup conversation memory
        self.chat_history = []
        
        # Setup prompt templates
        self.conversation_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=self.prompts.conversation
        )
        
        self.intent_prompt = PromptTemplate(
            input_variables=["input"],
            template=self.prompts.intent_detection
        )
        
        # Setup conversation chain
        self.conversation = (
            {"history": lambda x: self._get_chat_history(), "input": RunnablePassthrough()}
            | self.conversation_prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _get_chat_history(self) -> str:
        """Get formatted chat history."""
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history[-self.config.max_history_length:]])
    
    def _detect_intent(self, text: str) -> str:
        """Detect the intent of the user's request."""
        try:
            response = self.llm.invoke(self.intent_prompt.format(input=text)).strip().lower()
            logger.debug(f"🧠 Intent detected: '{response}'")
            
            if response in self.actions or response == "none":
                return response
            else:
                logger.warning(f"⚠️ Invalid intent detected: '{response}', defaulting to 'none'")
                return "none"
                
        except Exception as e:
            logger.error(f"❌ Error in intent detection: {e}")
            return "none"
    
    def _cancel_appointment(self, text: str) -> str:
        """Handle appointment cancellation intent."""
        return self.appointment_actions.cancel_appointment(text)
    
    def _schedule_appointment(self, text: str) -> str:
        """Handle appointment scheduling intent."""
        return self.appointment_actions.schedule_appointment(text)
    
    def _exit_conversation(self, text: str) -> str:
        """Handle exit command."""
        logger.info("👋 User has requested to exit the conversation")
        return "exit_signal"
    
    def listen(self) -> Optional[str]:
        """Listen for user input through voice."""
        return self.speech_recognizer.listen()
    
    def speak(self, text: str) -> None:
        """Speak the response."""
        self.text_to_speech.speak(text)
    
    def process(self, text: str) -> str:
        """Process user input and generate a response."""
        if not text:
            return self.prompts.greetings["repeat"]
        
        # Detect intent
        intent = self._detect_intent(text)
        
        # Execute action if required
        if intent in self.actions:
            logger.info(f"Executing action: {intent}")
            return self.actions[intent](text)
        
        # Generate normal response
        try:
            self.chat_history.append({"role": "Human", "content": text})
            response = self.conversation.invoke(text)
            self.chat_history.append({"role": "AI", "content": response})
            return response
        except Exception as e:
            logger.error(f"Error processing with LangChain: {e}")
            return self.prompts.greetings["error"]
    
    def run(self) -> None:
        """Run the assistant in a loop."""
        logger.info("="*60)
        logger.info("🤖 VOICE ASSISTANT READY")
        logger.info("="*60)
        logger.info("Simply speak to interact with the assistant")
        logger.info("Say 'exit', 'quit', or 'goodbye' to end the session")
        logger.info("="*60)
        
        logger.info(f"🤖 Assistant: \"{self.prompts.greetings['welcome']}\"")
        self.speak(self.prompts.greetings["welcome"])
        
        while True:
            try:
                logger.info("🎧 Listening...")
                user_input = self.listen()
                
                if user_input:
                    logger.info(f"👤 User: \"{user_input}\"")
                    logger.info("🤖 Processing...")
                    
                    response = self.process(user_input)
                    
                    if response == "exit_signal":
                        logger.info(f"👋 {self.prompts.greetings['farewell']}")
                        self.speak(self.prompts.greetings["farewell"])
                        break
                    
                    logger.info(f"🤖 Assistant: \"{response}\"")
                    self.speak(response)
                
            except KeyboardInterrupt:
                logger.info("👋 Goodbye! (Interrupted by user)")
                self.speak("Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {str(e)}")
                continue 