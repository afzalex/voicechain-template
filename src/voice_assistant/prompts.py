"""Prompt templates for the voice assistant."""
import json
import os
from typing import Dict

class PromptTemplates:
    """Collection of prompt templates loaded from files."""
    
    def __init__(self, prompts_dir: str = None):
        """Initialize prompt templates.
        
        Args:
            prompts_dir (str, optional): Directory containing prompt files. 
                Defaults to prompts directory in the same folder as this module.
        """
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        
        # Load conversation prompt
        with open(os.path.join(prompts_dir, "conversation.txt"), "r") as f:
            self.conversation = f.read()
        
        # Load intent detection prompt
        with open(os.path.join(prompts_dir, "intent_detection.txt"), "r") as f:
            self.intent_detection = f.read()
        
        # Load appointment extraction prompt
        with open(os.path.join(prompts_dir, "appointment_extraction.txt"), "r") as f:
            self.appointment_extraction = f.read()
        
        # Load scheduling extraction prompt
        with open(os.path.join(prompts_dir, "scheduling_extraction.txt"), "r") as f:
            self.scheduling_extraction = f.read()
        
        # Load title inference prompt
        with open(os.path.join(prompts_dir, "title_inference.txt"), "r") as f:
            self.title_inference = f.read()
        
        # Load greetings
        with open(os.path.join(prompts_dir, "greetings.json"), "r") as f:
            self.greetings = json.load(f) 