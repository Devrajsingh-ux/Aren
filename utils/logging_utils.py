"""
Logging utilities for AREN
"""

import logging
import os
from datetime import datetime

def setup_logger():
    """
    Set up and return a configured logger for AREN
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logger
    logger = logging.getLogger("aren")
    logger.setLevel(logging.INFO)
    
    # Create file handler with current date in filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"aren_{current_date}.log")
    file_handler = logging.FileHandler(log_file)
    
    # Create formatter and add to handler
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger() 