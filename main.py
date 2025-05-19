"""
AREN - Assistant for Regular and Extraordinary Needs
Main entry point for the AREN system
"""

import sys
import os
from brain.engine import ArenEngine
from utils.logging_utils import logger

def setup_environment():
    """Set up the environment for AREN"""
    # Create necessary directories if they don't exist
    dirs = [
        os.path.join(os.path.dirname(__file__), "logs"),
        os.path.join(os.path.dirname(__file__), "memory", "user_data")
    ]
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def main():
    """Main function for AREN"""
    setup_environment()
    
    logger.info("Starting A.R.E.N.")
    print("Welcome to A.R.E.N. (Assistant for Regular and Extraordinary Needs)")
    print("Type 'exit', 'quit', or 'bye' to end the session")
    
    try:
        engine = ArenEngine()
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("A.R.E.N.: Goodbye! Hope to see you again soon.")
                logger.info("AREN session ended by user")
                break
            
            response = engine.process_input(user_input)
            print(f"A.R.E.N.: {response}")
    except KeyboardInterrupt:
        print("\nA.R.E.N.: Session terminated by user. Goodbye!")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        print(f"A.R.E.N.: I encountered an error. Please restart me. ({str(e)})")
    finally:
        logger.info("A.R.E.N. session ended")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        print(f"Critical error: {str(e)}")
        sys.exit(1)
