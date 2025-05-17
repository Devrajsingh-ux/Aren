import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from features.command_processor import CommandProcessor
from gui.main_window import MainWindow
from brain.processor import RuleProcessor
from brain.speak import speak_text, stop_speaking, is_speaking

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
        self.speech_enabled = True  # Flag to control speech functionality

    def process_input(self, user_input: str) -> str:
        """Process user input and generate response."""
        try:
            # Convert input to lowercase for matching
            input_lower = user_input.lower()
            
            # Check for speech control commands
            if input_lower in ['stop speaking', 'shut up', 'be quiet']:
                stop_speaking()
                return "Speech stopped."
            elif input_lower in ['enable speech', 'start speaking']:
                self.speech_enabled = True
                return "Speech enabled."
            elif input_lower in ['disable speech', 'mute']:
                self.speech_enabled = False
                return "Speech disabled."
            
            # Check for stock market related queries
            if self.command_processor.stock_market.can_handle(user_input):
                response = self.command_processor.stock_market.process(user_input)
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for information requests
            if any(phrase in input_lower for phrase in ['what is', 'who is', 'tell me about', 'information about', 'who are', 'what are']):
                response = self.command_processor.process_command('info', [user_input])
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for personality-related commands
            if self.command_processor.personality.can_handle(user_input):
                response = self.command_processor.personality.process(user_input)
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for application opening command
            if input_lower.startswith('open '):
                app_name = user_input[5:].strip()  # Remove 'open ' prefix
                response = self.command_processor.process_command('open', [app_name])
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for application closing command
            if input_lower.startswith('close '):
                app_name = user_input[6:].strip()  # Remove 'close ' prefix
                response = self.command_processor.process_command('close', [app_name])
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for search commands
            if any(word in input_lower for word in ['search', 'find', 'look up', 'browse']):
                response = self.command_processor.process_command('search', [user_input])
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for time/date queries
            if 'time' in input_lower:
                response = self.command_processor.process_command('time', [])
                if self.speech_enabled:
                    speak_text(response)
                return response
            if 'date' in input_lower:
                response = self.command_processor.process_command('date', [])
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # Check for help request
            if 'help' in input_lower:
                response = self.command_processor.process_command('help', [])
                if self.speech_enabled:
                    speak_text(response)
                return response
            
            # If no specific command detected, process as regular input
            response = self.rule_processor.process_text(user_input)
            if self.speech_enabled:
                speak_text(response)
            return response
            
        except Exception as e:
            error_msg = "I encountered an error while processing your input."
            logger.error(f"Error processing input: {str(e)}")
            if self.speech_enabled:
                speak_text(error_msg)
            return error_msg

    def start_gui(self):
        """Start the GUI interface."""
        app = QApplication(sys.argv)
        self.gui = MainWindow(self)
        self.gui.show()
        sys.exit(app.exec())

    def start_console(self):
        """Start the console interface."""
        print("A.R.E.N initialized. Type 'exit' to quit.")
        if self.speech_enabled:
            speak_text("A.R.E.N initialized. How can I help you?")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == 'exit':
                    goodbye_msg = "Goodbye!"
                    print(goodbye_msg)
                    if self.speech_enabled:
                        speak_text(goodbye_msg)
                    break
                
                response = self.process_input(user_input)
                print(f"A.R.E.N: {response}")
                
            except KeyboardInterrupt:
                goodbye_msg = "\nGoodbye!"
                print(goodbye_msg)
                if self.speech_enabled:
                    speak_text(goodbye_msg)
                break
            except Exception as e:
                error_msg = "An error occurred. Please try again."
                logger.error(f"Error in console interface: {str(e)}")
                print(error_msg)
                if self.speech_enabled:
                    speak_text(error_msg)

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