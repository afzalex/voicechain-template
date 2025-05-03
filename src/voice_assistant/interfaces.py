"""Interfaces for voice assistant components."""
from abc import ABC, abstractmethod
from typing import Optional

class SpeechRecognizerInterface(ABC):
    """Interface for speech recognition components."""
    
    @abstractmethod
    def listen(self) -> Optional[str]:
        """Listen for and transcribe speech.
        
        Returns:
            Optional[str]: Transcribed text or None if no speech detected
        """
        pass

class TextToSpeechInterface(ABC):
    """Interface for text-to-speech components."""
    
    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech and play it.
        
        Args:
            text (str): Text to speak
        """
        pass

class LLMInterface(ABC):
    """Interface for language model components."""
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response to the given prompt.
        
        Args:
            prompt (str): Input prompt
            
        Returns:
            str: Generated response
        """
        pass
    
    @abstractmethod
    def detect_intent(self, text: str) -> str:
        """Detect the intent of the given text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Detected intent
        """
        pass

class ActionHandlerInterface(ABC):
    """Interface for action handlers."""
    
    @abstractmethod
    def handle_action(self, intent: str, text: str) -> str:
        """Handle a specific action based on intent.
        
        Args:
            intent (str): Detected intent
            text (str): Input text
            
        Returns:
            str: Response to the action
        """
        pass 