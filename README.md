# AI Voice Assistant

A real-time voice assistant that converts speech to text using OpenAI's Whisper, processes it using Llama 3 via Ollama, and responds with synthesized speech.

## Features

- Real-time speech-to-text conversion using Whisper
- Natural language processing using Llama 3
- Text-to-speech response
- Simple and intuitive interface

## Prerequisites

- Python 3.8 or higher
- Conda package manager
- Ollama installed and running locally
- Llama 3 model pulled in Ollama

## Installation

1. Clone this repository
2. Create and activate the conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate voice-assistant
   ```
3. Make sure Ollama is running and Llama 3 is installed:
   ```bash
   ollama pull llama2
   ```

## Usage

Run the main script:
```bash
python src/main.py
```

Press Ctrl+C to exit the program.

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