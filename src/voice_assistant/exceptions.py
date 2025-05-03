"""Custom exceptions for the voice assistant."""

class VoiceAssistantError(Exception):
    """Base exception for voice assistant errors."""
    pass

class SpeechRecognitionError(VoiceAssistantError):
    """Exception raised for speech recognition errors."""
    pass

class TTSGenerationError(VoiceAssistantError):
    """Exception raised for text-to-speech generation errors."""
    pass

class LLMConnectionError(VoiceAssistantError):
    """Exception raised for LLM connection errors."""
    pass

class LLMResponseError(VoiceAssistantError):
    """Exception raised for LLM response errors."""
    pass

class ActionHandlerError(VoiceAssistantError):
    """Exception raised for action handler errors."""
    pass

class ConfigurationError(VoiceAssistantError):
    """Exception raised for configuration errors."""
    pass 