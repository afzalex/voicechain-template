"""Voice Assistant package - A modular voice agent with speech recognition and TTS capabilities."""
# Import at usage time to avoid circular imports
__all__ = ["VoiceAgent"]

def VoiceAgent(config=None):
    """Factory function to create and return a VoiceAgent instance.
    
    Args:
        config: Optional configuration object to pass to the VoiceAgent.
    """
    from .core.agent import VoiceAgent as _VoiceAgent
    return _VoiceAgent(config=config) 