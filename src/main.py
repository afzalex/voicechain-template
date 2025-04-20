import time
from speech_recognition import SpeechRecognizer
from llm_processor import LLMProcessor
from text_to_speech import TextToSpeech

def main():
    print("Initializing AI Voice Assistant...")
    
    # Initialize components
    speech_recognizer = SpeechRecognizer()
    llm_processor = LLMProcessor()
    tts = TextToSpeech()
    
    print("\nAI Voice Assistant is ready!")
    print("Press Ctrl+C to exit")
    print("-" * 50)
    
    try:
        while True:
            # Listen for speech
            text = speech_recognizer.listen()
            
            if text:
                # Process with LLM
                response = llm_processor.process_text(text)
                
                # Print the response before speaking
                print("\nAssistant: " + response)
                print("-" * 50)
                
                # Speak the response
                tts.speak(response)
            
            # Small delay to prevent CPU overuse
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 