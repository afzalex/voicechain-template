"""Configuration management for the voice assistant."""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class SpeechConfig:
    """Speech recognition configuration."""
    vad_mode: int = 3
    sample_rate: int = 16000
    whisper_model: str = "base"
    min_speech_frames: int = 5
    end_silence_sec: float = 4.0
    max_record_sec: float = 60.0

@dataclass
class TTSConfig:
    """Text-to-speech configuration."""
    model_name: str = "tts_models/en/vctk/vits"
    speaker: str = "p360"
    sample_rate: int = 22050

@dataclass
class LLMConfig:
    """Language model configuration."""
    model: str = "llama3"
    base_url: str = "http://localhost:11434"
    max_tokens: int = 150
    temperature: float = 0.7

@dataclass
class AssistantConfig:
    """Main assistant configuration."""
    speech: SpeechConfig = SpeechConfig()
    tts: TTSConfig = TTSConfig()
    llm: LLMConfig = LLMConfig()
    max_history_length: int = 10
    debug_mode: bool = False

def load_config() -> AssistantConfig:
    """Load configuration from environment variables with defaults."""
    return AssistantConfig(
        speech=SpeechConfig(
            vad_mode=int(os.getenv("VAD_MODE", "3")),
            sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
            whisper_model=os.getenv("WHISPER_MODEL", "base"),
            min_speech_frames=int(os.getenv("MIN_SPEECH_FRAMES", "5")),
            end_silence_sec=float(os.getenv("END_SILENCE_SEC", "4.0")),
            max_record_sec=float(os.getenv("MAX_RECORD_SEC", "60.0"))
        ),
        tts=TTSConfig(
            model_name=os.getenv("TTS_MODEL", "tts_models/en/vctk/vits"),
            speaker=os.getenv("TTS_SPEAKER", "p360"),
            sample_rate=int(os.getenv("TTS_SAMPLE_RATE", "22050"))
        ),
        llm=LLMConfig(
            model=os.getenv("LLM_MODEL", "llama3"),
            base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "150")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        ),
        max_history_length=int(os.getenv("MAX_HISTORY_LENGTH", "10")),
        debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
    ) 