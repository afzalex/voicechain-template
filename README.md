# Voice Assistant

A simple voice assistant that uses speech recognition and text-to-speech to interact with users.

## Features

- Speech recognition using OpenAI's Whisper model (local)
- Text-to-speech for voice output
- Automatic fallback to text input when voice recognition fails
- Basic conversation capabilities using Ollama LLM
- Runs on macOS with native audio recording support

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/voice-assistant.git
cd voice-assistant
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Install and run Ollama:
```bash
# Download from https://ollama.com/
ollama serve
ollama pull llama3
```

## Usage

Run the voice assistant:
```bash
python src/main.py
```

For troubleshooting, you can run in debug mode:
```bash
python src/main.py --debug
```

The voice assistant will:
1. Listen for your voice input using Whisper for local speech recognition
2. Fall back to text input if speech recognition fails
3. Process your request using the Ollama LLM
4. Respond with voice and text

Commands:
- Say "hello" or "hi" to get a greeting
- Say "bye", "exit", or "quit" to end the conversation
- Ask questions to get responses from the LLM

## Requirements

- Python 3.8 or higher
- macOS (for native audio recording, other platforms may require additional setup)
- Ollama running locally with the llama3 model

## License

MIT