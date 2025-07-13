"""
AREN Runner Script
This script can run AREN in different modes:
1. GUI mode (default)
2. CLI mode
3. API server mode
4. Combined mode (API server + GUI)
"""

import sys
import threading
import time
from main import run_cli_mode, setup_environment
from api_server import run_server
from utils.logging_utils import logger

def print_usage():
    """Print usage information"""
    print("AREN Runner Script")
    print("Usage: python run_aren.py [mode] [port]")
    print("Modes:")
    print("  --gui       : Run AREN in GUI mode (default)")
    print("  --cli       : Run AREN in CLI mode")
    print("  --api       : Run AREN as API server only")
    print("  --combined  : Run both API server and GUI")
    print("Options:")
    print("  port        : Port number for API server (default: 5000)")

def run_api_server(port=5000):
    """Run the API server in a separate thread"""
    api_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    api_thread.start()
    logger.info(f"API server started on port {port}")
    return api_thread

def main():
    """Main function"""
    # Set up environment
    setup_environment()
    
    # Parse command line arguments
    mode = "--gui"  # Default mode
    port = 5000     # Default port
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            logger.error(f"Invalid port number: {sys.argv[2]}")
            print_usage()
            return
    
    # Run AREN in the specified mode
    if mode == "--gui":
        logger.info("Starting AREN in GUI mode")
        # Import GUI mode only when needed
        from main import run_gui_mode
        run_gui_mode()
    elif mode == "--cli":
        logger.info("Starting AREN in CLI mode")
        run_cli_mode()
    elif mode == "--api":
        logger.info("Starting AREN as API server")
        run_server(port=port)
    elif mode == "--combined":
        logger.info("Starting AREN in combined mode (API + GUI)")
        api_thread = run_api_server(port)
        time.sleep(1)  # Give the API server a moment to start
        # Import GUI mode only when needed
        from main import run_gui_mode
        run_gui_mode()
    else:
        logger.error(f"Unknown mode: {mode}")
        print_usage()

if __name__ == "__main__":
    main() 