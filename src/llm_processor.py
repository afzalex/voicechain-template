import os
import requests
import json

class LLMProcessor:
    def __init__(self):
        """
        Initialize the LLM processor to use Llama 3 through Ollama.
        """
        self.model = "llama3"
        self.api_url = "http://localhost:11434/api/generate"
        
        # Test connection to Ollama
        try:
            self._check_ollama_connection()
            print(f"Connected to Ollama. Using model: {self.model}")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            raise e
    
    def _check_ollama_connection(self):
        """
        Check if Ollama is running and the model is available.
        """
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                raise ConnectionError("Ollama is not running or not accessible")
            
            # Check if the model is available
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            if self.model not in model_names:
                print(f"Note: Using model '{self.model}'. Make sure it's installed with 'ollama pull {self.model}'")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to Ollama. Make sure it's running.")
    
    def process_text(self, text):
        """
        Process text using Llama 3 through Ollama.
        
        Args:
            text (str): Input text to process
            
        Returns:
            str: Processed response from the model
        """
        try:
            # Prepare the request to Ollama
            payload = {
                "model": self.model,
                "prompt": text,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 100
                }
            }
            
            # Send the request to Ollama
            response = requests.post(self.api_url, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"Ollama API returned status code {response.status_code}: {response.text}")
            
            # Extract the response text
            response_data = response.json()
            response_text = response_data.get("response", "").strip()
            
            # Ensure response is not too long
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
            
        except Exception as e:
            print(f"Error with Llama 3: {e}")
            raise e 