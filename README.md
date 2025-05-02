# VoiceChain-Template

A comprehensive template project for building voice-based AI applications using LangChain. This project demonstrates how to integrate voice input/output with modern AI frameworks, providing a solid foundation for various voice-based applications.

## Features

- **Modern LangChain Integration**
  - Uses latest LangChain packages (langchain-core, langchain-community, langchain-ollama)
  - Demonstrates best practices for LangChain implementation
  - Example of intent detection and conversation management

- **Voice Processing**
  - **Speech Recognition** using Whisper and WebRTC VAD
  - **Text-to-Speech** with platform-specific optimizations
  - Voice Activity Detection (VAD) for efficient processing

- **AI Capabilities**
  - Local LLM integration with Ollama
  - Intent detection and natural language processing
  - Extensible conversation management
  - Example implementation of appointment scheduling (can be replaced with other use cases)

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Conda (recommended) or pip
- Ollama installed and running
- Microphone and speakers

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd voicechain-template
   ```

2. Set up the conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate voice-assistant-py310
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Ollama:
   ```bash
   # Start Ollama service
   ollama serve
   
   # Pull the required model
   ollama pull llama3
   ```

### Running the Application

1. **Development Mode**
   ```bash
   # Basic mode
   python src/main.py
   
   # Debug mode with detailed logs
   python src/main.py --debug
   ```

2. **Production Mode**
   ```bash
   # Make the script executable (one-time setup)
   chmod +x voice-assistant
   
   # Run the application
   ./voice-assistant
   ```

3. **Global Installation (Optional)**
   ```bash
   # Copy to a directory in your PATH
   sudo cp voice-assistant /usr/local/bin/
   
   # Run from anywhere
   voice-assistant
   ```

## Project Structure

```
voicechain-template/
├── src/
│   ├── main.py                 # Application entry point
│   ├── test_speech_rec.py      # Speech recognition test script
│   ├── test_tts.py            # Text-to-speech test script
│   └── voice_assistant/        # Main package
│       ├── core/               # Core components
│       │   ├── agent.py        # Main voice agent and LangChain integration
│       │   ├── appointment_actions.py  # Example use case implementation
│       │   ├── speech_recognition.py   # Speech recognition
│       │   └── text_to_speech.py       # Text-to-speech
│       └── utils/              # Utilities
│           └── date_utils.py   # Date handling utilities
├── requirements.txt            # Python dependencies
├── environment.yml            # Conda environment configuration
└── voice-assistant           # Production script
```

## Getting Started Guide

### 1. Understanding the Components

The project consists of several key components:

- **Voice Processing**
  - `speech_recognition.py`: Handles voice input using Whisper and VAD
  - `text_to_speech.py`: Manages voice output using TTS
  - Test these components using `test_speech_rec.py` and `test_tts.py`

- **AI Integration**
  - `agent.py`: Core LangChain integration and conversation management
  - `appointment_actions.py`: Example implementation of appointment scheduling

### 2. Testing Individual Components

Before running the full application, you can test individual components:

```bash
# Test speech recognition
python src/test_speech_rec.py

# Test text-to-speech
python src/test_tts.py
```

### 3. Customizing the Application

1. **Replace the Example Use Case**
   - Modify `appointment_actions.py` for your specific use case
   - Update intent detection in `agent.py`
   - Adjust the conversation chain as needed

2. **Add New Features**
   - Integrate additional LangChain tools
   - Add new voice processing capabilities
   - Implement custom memory management

### 4. Troubleshooting

Common issues and solutions:

1. **Speech Recognition Issues**
   - Check microphone permissions
   - Ensure proper audio device selection
   - Verify VAD settings in `speech_recognition.py`

2. **Ollama Connection Issues**
   - Verify Ollama is running: `ollama serve`
   - Check `OLLAMA_HOST` environment variable
   - Ensure llama3 model is pulled: `ollama pull llama3`

3. **Text-to-Speech Issues**
   - Check speaker permissions
   - Verify audio output device
   - Adjust TTS settings in `text_to_speech.py`

## Customization

This template can be customized for various use cases:

1. **Replace the Example Use Case**
   - The appointment scheduling functionality in `appointment_actions.py` can be replaced with your own use case
   - Update the intent detection in `agent.py` to recognize new commands
   - Modify the conversation chain to handle new types of interactions

2. **Add New Features**
   - Integrate additional LangChain tools and agents
   - Add new voice processing capabilities
   - Implement custom memory management
   - Add support for different LLM providers

3. **Extend the UI**
   - Add a web interface
   - Implement a mobile app
   - Create a desktop application

## Environment Variables

- `OLLAMA_HOST`: URL for the Ollama service (default: http://localhost:11434)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)