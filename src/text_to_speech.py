from Foundation import *
from AppKit import *
import objc

class TextToSpeech:
    def __init__(self):
        self.synthesizer = NSSpeechSynthesizer.alloc().init()
        
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to be spoken
        """
        try:
            print(f"Speaking: {text}")
            self.synthesizer.startSpeakingString_(text)
            while self.synthesizer.isSpeaking():
                NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
        except Exception as e:
            print(f"Error in text-to-speech: {e}") 