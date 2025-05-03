"""Logging configuration for the voice assistant."""
import logging
import sys
from typing import Optional

def setup_logging(debug: bool = False, quiet: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        debug (bool): Enable debug mode
        quiet (bool): Enable quiet mode
    """
    # Create formatters
    debug_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    info_formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on mode
    if debug:
        console_handler.setFormatter(debug_formatter)
        level = logging.DEBUG
    elif quiet:
        console_handler.setFormatter(debug_formatter)
        level = logging.WARNING
    else:
        console_handler.setFormatter(info_formatter)
        level = logging.INFO
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(level)
    
    # Configure voice-assistant logger specifically
    voice_logger = logging.getLogger("voice-assistant")
    voice_logger.setLevel(level)
    voice_logger.propagate = True
    
    # Log configuration
    if debug:
        root_logger.debug("Debug mode enabled")
    elif quiet:
        root_logger.warning("Quiet mode enabled")
    else:
        root_logger.info("Normal logging mode enabled") 