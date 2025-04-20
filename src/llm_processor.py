import requests
import json
import os
from dotenv import load_dotenv
import random

class LLMProcessor:
    def __init__(self, model_name="llama3", base_url="http://localhost:11434"):
        load_dotenv()
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.use_ollama = True
        
        # Test Ollama connection and get available models
        try:
            response = requests.get(f"{base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            
            # Find the best available model
            available_models = [model['name'] for model in models]
            print(f"Available models: {', '.join(available_models)}")
            
            if model_name in available_models:
                self.model_name = model_name
                print(f"Using model: {model_name}")
            elif 'llama3' in available_models:
                self.model_name = 'llama3'
                print("Using model: llama3")
            elif 'llama2' in available_models:
                self.model_name = 'llama2'
                print("Using model: llama2")
            else:
                self.model_name = available_models[0] if available_models else model_name
                print(f"Using model: {self.model_name}")
                
            print("Connected to Ollama successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            print("Ollama is not running. Using fallback responses.")
            self.use_ollama = False
    
    def get_fallback_response(self, text):
        """
        Provide a fallback response when Ollama is not available.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Fallback response
        """
        text = text.lower().strip()
        
        # Simple pattern matching for common queries with more natural responses
        if any(word in text for word in ['hello', 'hi', 'hey']):
            responses = [
                "Hey there! What's on your mind?",
                "Hi! How can I help you today?",
                "Hello! What can I do for you?"
            ]
            return random.choice(responses)
        elif any(word in text for word in ['how are you', 'how are you doing']):
            responses = [
                "I'm doing great! How about you?",
                "Pretty good! What's up with you?",
                "All good here! How are you?"
            ]
            return random.choice(responses)
        elif any(word in text for word in ['bye', 'goodbye', 'see you']):
            responses = [
                "See you later!",
                "Take care!",
                "Bye! Have a great one!"
            ]
            return random.choice(responses)
        elif 'time' in text:
            return "I'd love to tell you the time, but I need Ollama running for that. Want me to help you set it up?"
        elif 'weather' in text:
            return "I can check the weather for you once Ollama's running. Need help getting that set up?"
        elif 'help' in text:
            return "I can chat with you about basic stuff right now. For more cool features, we'll need to get Ollama running. Want to try that?"
        else:
            responses = [
                "Hmm, I'd love to help with that, but I need Ollama running for the fancy stuff. Want to try 'help' to see what I can do now?",
                "That's interesting! For more advanced responses, we'll need Ollama. Want to see what I can do without it?",
                "I can help with that once Ollama's running. For now, try asking for 'help' to see my basic features!"
            ]
            return random.choice(responses)
    
    def process_text(self, text):
        """
        Process text using the LLM model via Ollama or fallback to simple responses.
        
        Args:
            text (str): Input text to process
            
        Returns:
            str: Processed response from the model
        """
        if not self.use_ollama:
            return self.get_fallback_response(text)
            
        try:
            # Add instruction for natural, conversational responses
            prompt = f"""You are a friendly and helpful AI assistant. Please respond to this in a natural, conversational way, as if talking to a friend. Keep it brief but engaging:

{text}"""
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,  # Slightly increased for more natural variation
                    "num_predict": 100,  # Keep responses concise
                    "top_p": 0.9,  # Allow for more natural language variation
                    "repeat_penalty": 1.1  # Reduce repetition
                }
            }
            
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', 'No response from model')
            
            # Ensure response is not too long while preserving natural flow
            words = response_text.split()
            if len(words) > 50:
                # Try to find a natural breaking point
                break_point = 50
                for i in range(45, 55):  # Look for sentence end near 50 words
                    if i < len(words) and words[i].endswith(('.', '!', '?')):
                        break_point = i + 1
                        break
                response_text = ' '.join(words[:break_point]) + "..."
                
            return response_text
            
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return self.get_fallback_response(text)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "Oops! Something went wrong. Want to try that again?" 