#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from voice_agent import VoiceAgent
import logging

def main():
    """Run the voice agent application with WebRTC VAD"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the voice agent application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Configure logging based on debug mode
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s [%(levelname)s] %(message)s')
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    try:
        # Create and run the voice agent
        agent = VoiceAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\nExiting voice agent...")
    except Exception as e:
        print(f"Error running voice agent: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 