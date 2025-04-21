# AI Voice Assistant

A voice assistant that uses Whisper for speech recognition, Llama 3 (via Ollama) for processing, and Google Text-to-Speech for responses.

## Features

- Real-time speech-to-text conversion using Whisper
- Natural language processing using Llama 3
- Text-to-speech response
- Simple and intuitive interface

## Prerequisites

- Python 3.8 or higher
- ffmpeg (for audio recording and playback)
- Ollama with the llama3 model installed

## Setup

1. Clone this repository
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Install ffmpeg
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

4. Install and run Ollama
   - Follow the instructions at [ollama.ai](https://ollama.ai) to install Ollama
   - Run Ollama: `ollama serve`
   - In a separate terminal, pull the llama3 model: `ollama pull llama3`

## Usage

Run the voice assistant:
```bash
python src/run.py
```

- The assistant will listen for your voice
- Speak clearly into your microphone
- The assistant will process your request and respond verbally

## Permissions

- **Microphone**: The application needs permission to access your microphone
- If you encounter permission issues, follow the instructions provided when the error occurs

## Troubleshooting

- **Microphone not working**: Check your system permissions for microphone access
- **Ollama connection error**: Make sure Ollama is running with `ollama serve`
- **TTS errors**: Check your internet connection as Google TTS requires internet access

## Project Structure

```
.
├── README.md
├── requirements.txt
├── environment.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── speech_recognition.py
│   ├── llm_processor.py
│   └── text_to_speech.py
```

## Notes

- The speech recognition uses Whisper's "base" model by default. You can change this in the `SpeechRecognizer` class initialization.
- The first run will download the Whisper model, which might take some time depending on your internet connection.
- Audio recording is set to 10 seconds by default. You can adjust this in the `RECORD_SECONDS` parameter in the `SpeechRecognizer` class.

## License

MIT License 