#!/bin/bash

echo "Setting up voice assistant dependencies for macOS..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed. Updating..."
    brew update
fi

# Install ffmpeg (for audio recording)
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing ffmpeg for audio recording..."
    brew install ffmpeg
else
    echo "ffmpeg is already installed."
fi

# Install sox (alternative for audio recording)
if ! command -v sox &> /dev/null; then
    echo "Installing sox as an alternative audio tool..."
    brew install sox
else
    echo "sox is already installed."
fi

# Install PortAudio (needed for sounddevice to work properly)
brew install portaudio

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install numpy scipy  # Additional packages for audio processing

echo ""
echo "Setup completed!"
echo "You can now run the test script with:"
echo "python src/test.py"
echo ""
echo "Or run the voice assistant with:"
echo "python src/main.py"
echo ""
echo "If you encounter any issues with Python packages, try:"
echo "pip install --upgrade sounddevice numpy scipy"