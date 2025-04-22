#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from voice_assistant import VoiceAgent
import logging

def main():
    """Run the voice agent application with WebRTC VAD"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the voice agent application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--quiet", action="store_true", help="Hide info logs")
    args = parser.parse_args()
    
    # Create a logger named 'main'
    main_logger = logging.getLogger("main")
    
    # Configure logging system
    if args.debug:
        # Debug mode: show detailed logs including from libraries
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        # Ensure voice-assistant logger shows debug messages
        voice_logger = logging.getLogger("voice-assistant")
        voice_logger.setLevel(logging.DEBUG)
        main_logger.setLevel(logging.DEBUG)
        
        # Show debug level in banner
        log_level = "DEBUG"
    elif args.quiet:
        # Quiet mode: only show warnings and errors
        logging.basicConfig(level=logging.WARNING,
                           format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        main_logger.setLevel(logging.WARNING)
        log_level = "QUIET"
    else:
        # Default mode: show info logs with emoji and formatted
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s [%(name)s] %(message)s')
        main_logger.setLevel(logging.INFO)
        log_level = "INFO"
    
    # Print startup banner with main logger
    main_logger.info("="*60)
    main_logger.info("🎙️  VOICE ASSISTANT")
    main_logger.info("="*60)
    main_logger.info(f"Starting with log level: {log_level}")
    main_logger.info("Run with --debug for more detailed logs")
    main_logger.info("Run with --quiet to hide info logs")
    main_logger.info("="*60)
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    try:
        # Create and run the voice agent
        agent = VoiceAgent()
        agent.run()
    except KeyboardInterrupt:
        main_logger.info("Exiting voice assistant...")
    except Exception as e:
        main_logger.error(f"Error running voice assistant: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 