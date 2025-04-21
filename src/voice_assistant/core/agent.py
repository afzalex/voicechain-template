"""Main Voice Assistant Agent that coordinates speech, TTS, and other components."""
import os
import logging
import warnings
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

from .speech_recognition import SpeechRecognizer
from .text_to_speech import TextToSpeech
from .appointment_actions import AppointmentActions
from ..utils.date_utils import normalize_date

# Get logger
logger = logging.getLogger("voice-assistant")

class VoiceAgent:
    """Main voice assistant agent that coordinates speech recognition and text-to-speech."""
    
    def __init__(self):
        """Initialize the voice agent with required components."""
        # Initialize components
        self.speech_recognizer = SpeechRecognizer(vad_mode=3, whisper_model="base")
        self.text_to_speech = TextToSpeech()
        
        # Initialize LangChain components
        try:
            self._init_langchain()
            
            # Initialize appointment actions
            self.appointment_actions = AppointmentActions(self.llm)
            
            # Available actions
            self.actions = {
                "cancel_appointment": self._cancel_appointment,
                "schedule_appointment": self._schedule_appointment,
                "exit": self._exit_conversation
            }
            
            logger.info("Voice Agent initialized!")
        except Exception as e:
            logger.error(f"Error initializing Voice Agent: {e}")
            raise
    
    def _init_langchain(self):
        """Initialize LangChain components for conversation and intent detection."""
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
                - schedule_appointment: When the user wants to schedule or book a new appointment
                - exit: When the user wants to end the conversation, say goodbye, or quit
                - none: When no specific action is required, just respond normally
                
                User request: {input}
                
                Return only the action name without explanation. For example: "cancel_appointment", "schedule_appointment", "exit", or "none".
                Action:"""
            )
            
            # Setup conversation chain with warning suppression
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
        """Use the LLM to detect the intent of the user's request.
        
        Args:
            text (str): User input text
            
        Returns:
            str: Detected intent name
        """
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
        """Handle appointment cancellation intent.
        
        Args:
            text (str): User's cancellation request
            
        Returns:
            str: Response to the user
        """
        return self.appointment_actions.cancel_appointment(text)
    
    def _schedule_appointment(self, text):
        """Handle appointment scheduling intent.
        
        Args:
            text (str): User's scheduling request
            
        Returns:
            str: Response to the user
        """
        return self.appointment_actions.schedule_appointment(text, normalize_date)
    
    def _exit_conversation(self, text):
        """Handle exit command.
        
        Args:
            text (str): User's exit request
            
        Returns:
            str: Special exit signal
        """
        logger.info("👋 User has requested to exit the conversation")
        return "exit_signal"  # Special return value to signal exit
    
    def listen(self):
        """Listen for user input through voice.
        
        Returns:
            str or None: Transcribed user speech
        """
        return self.speech_recognizer.listen()
    
    def speak(self, text):
        """Speak the response.
        
        Args:
            text (str): Text to speak
        """
        self.text_to_speech.speak(text)
    
    def process(self, text):
        """Process user input and generate a response.
        
        Args:
            text (str): User input text
            
        Returns:
            str: Response to the user
        """
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
        """Run the assistant in a loop."""
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