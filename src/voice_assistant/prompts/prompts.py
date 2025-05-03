"""Prompt templates for the voice assistant."""
import json
import os
from typing import Dict

class PromptTemplates:
    """Collection of prompt templates for different tasks."""
    
    def __init__(self):
        """Initialize prompt templates from files."""
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        # Load conversation template
        with open(os.path.join(self.templates_dir, "conversation.txt"), "r") as f:
            self.conversation = f.read().strip()
        
        # Load intent detection template
        with open(os.path.join(self.templates_dir, "intent_detection.txt"), "r") as f:
            self.intent_detection = f.read().strip()
        
        # Load appointment extraction template
        with open(os.path.join(self.templates_dir, "appointment_extraction.txt"), "r") as f:
            self.appointment_extraction = f.read().strip()
        
        # Load scheduling extraction template
        with open(os.path.join(self.templates_dir, "scheduling_extraction.txt"), "r") as f:
            self.scheduling_extraction = f.read().strip()
        
        # Load title inference template
        with open(os.path.join(self.templates_dir, "title_inference.txt"), "r") as f:
            self.title_inference = f.read().strip()
        
        # Load greetings
        with open(os.path.join(self.templates_dir, "greetings.json"), "r") as f:
            self.greetings: Dict[str, str] = json.load(f) 