# Voice Assistant

A modular voice assistant with speech recognition, text-to-speech, and appointment scheduling capabilities.

## Features

- **Speech Recognition** using Whisper and WebRTC VAD
- **Text-to-Speech** with platform-specific optimizations
- **Appointment Management**:
  - Schedule appointments with date, time, and title
  - Cancel appointments
  - Infer appointment titles and normalize date references

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd voice-assistant
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

4. Make sure you have Ollama running:
   ```bash
   ollama serve
   ollama pull llama3
   ```

## Usage

### Development Mode

Run the voice assistant:

```bash
python src/main.py
```

For debug mode:

```bash
python src/main.py --debug
```

### Production Mode

For production use, we provide a convenient executable script:

```bash
# Make the script executable (one-time setup)
chmod +x voice-assistant

# Run the application
./voice-assistant
```

You can also place the script in your PATH for global access:

```bash
# Copy to a directory in your PATH (requires admin permission)
sudo cp voice-assistant /usr/local/bin/

# Then run from anywhere
voice-assistant
```

The script automatically:
- Activates the correct conda environment
- Runs the application with proper paths
- Passes any command-line arguments to the application

## Project Structure

```
src/
├── main.py                 # Entry point
├── voice_assistant/        # Main package
│   ├── __init__.py
│   ├── core/               # Core components
│   │   ├── __init__.py
│   │   ├── agent.py        # Main voice agent
│   │   ├── appointment_actions.py  # Appointment functionality
│   │   ├── speech_recognition.py   # Speech recognition
│   │   └── text_to_speech.py       # Text-to-speech
│   └── utils/              # Utilities
│       ├── __init__.py
│       └── date_utils.py   # Date handling utilities
```

## Voice Commands

- **Schedule an appointment**: "Schedule a doctor's appointment tomorrow at 2 PM"
- **Cancel an appointment**: "Cancel my dentist appointment on Friday"
- **Ask questions**: "What's the weather like today?"
- **Exit**: "Goodbye", "Exit", or "Quit"

## Environment Variables

- `OLLAMA_HOST`: URL for the Ollama service (default: http://localhost:11434)

## License

[MIT License](LICENSE)