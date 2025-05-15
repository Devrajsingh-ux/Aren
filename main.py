import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from features.command_processor import CommandProcessor
from gui.main_window import MainWindow
from brain.processor import RuleProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AREN:
    def __init__(self):
        self.rule_processor = RuleProcessor()
        self.command_processor = CommandProcessor()
        self.gui = None

    def process_input(self, user_input: str) -> str:
        """Process user input and generate response."""
        try:
            # Convert input to lowercase for matching
            input_lower = user_input.lower()
            
            # Check for personality-related commands first
            if self.command_processor.personality.can_handle(user_input):
                return self.command_processor.personality.process(user_input)
            
            # Check for application opening command
            if input_lower.startswith('open '):
                app_name = user_input[5:].strip()  # Remove 'open ' prefix
                return self.command_processor.process_command('open', [app_name])
            
            # Check for search commands
            if any(word in input_lower for word in ['search', 'find', 'look up', 'browse']):
                return self.command_processor.process_command('search', [user_input])
            
            # Check for time/date queries
            if 'time' in input_lower:
                return self.command_processor.process_command('time', [])
            if 'date' in input_lower:
                return self.command_processor.process_command('date', [])
            
            # Check for help request
            if 'help' in input_lower:
                return self.command_processor.process_command('help', [])
            
            # Check for information request
            if any(phrase in input_lower for phrase in ['who is', 'tell me about', 'information about', 'what is', 'who are']):
                return self.command_processor.process_command('info', [user_input])
            
            # If no specific command detected, process as regular input
            return self.rule_processor.process_text(user_input)
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return "I encountered an error while processing your input."

    def start_gui(self):
        """Start the GUI interface."""
        app = QApplication(sys.argv)
        self.gui = MainWindow(self)
        self.gui.show()
        sys.exit(app.exec())

    def start_console(self):
        """Start the console interface."""
        print("A.R.E.N initialized. Type 'exit' to quit.")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                
                response = self.process_input(user_input)
                print(f"A.R.E.N: {response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in console interface: {str(e)}")
                print("An error occurred. Please try again.")

def main():
    """Main entry point for the application."""
    try:
        aren = AREN()
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == '--console':
            aren.start_console()
        else:
            aren.start_gui()
            
    except Exception as e:
        logger.error(f"Error starting A.R.E.N: {str(e)}")
        print("Failed to start A.R.E.N. Please check the logs for details.")

if __name__ == "__main__":
    main() 