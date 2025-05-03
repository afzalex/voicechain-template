#!/usr/bin/env python3
"""Main entry point for the voice assistant application."""
import logging
import sys

# Now import other modules
import argparse
from dotenv import load_dotenv
from voice_assistant import VoiceAgent
from voice_assistant.config import load_config
from voice_assistant.exceptions import VoiceAssistantError
from voice_assistant.logging import setup_logging

def main():
    """Run the voice agent application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the voice agent application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--quiet", action="store_true", help="Hide info logs")
    args = parser.parse_args()
    
    # Setup logging based on command line arguments
    setup_logging(debug=args.debug, quiet=args.quiet)
    logger = logging.getLogger("voice-assistant")
    logger.debug("Logging setup complete")
    
    # Load environment variables
    logger.debug("Loading environment variables...")
    load_dotenv()
    
    try:
        # Load configuration
        logger.debug("Loading configuration...")
        config = load_config()
        logger.debug("Configuration loaded successfully")
        
        # Create and run the voice agent
        logger.debug("Creating voice agent...")
        agent = VoiceAgent(config=config)
        logger.debug("Voice agent created successfully")
        
        logger.debug("Starting voice agent...")
        agent.run()
        
    except KeyboardInterrupt:
        logger.info("\nExiting voice assistant...")
    except VoiceAssistantError as e:
        logger.error(f"Error running voice assistant: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 