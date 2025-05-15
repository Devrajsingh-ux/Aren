import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class RuleProcessor:
    def __init__(self):
        self.rules = {
            r'hi|hello|hey': 'Hello! How can I help you today?',
            r'how are you': 'I am functioning well, thank you for asking!',
            r'bye|goodbye': 'Goodbye! Have a great day!',
            r'thank you|thanks': 'You\'re welcome!',
            r'what time is it': lambda: f'The current time is {datetime.datetime.now().strftime("%I:%M %p")}',
            r'what is the date': lambda: f'Today is {datetime.datetime.now().strftime("%A, %B %d, %Y")}',
            r'help': 'I can help you with various tasks. Type /help to see available commands.',
            r'who are you': 'I am A.R.E.N (Advanced Response Engine with Neural processing), your personal assistant. I can help you with various tasks and information.',
            r'what can you do': 'I can help you with various tasks like getting time and date, setting reminders, searching the web, and more. Type /help to see all available commands.'
        }
        self.learned_patterns = {}
        self._load_learning_data()

    def _load_learning_data(self):
        """Load learned patterns from file."""
        try:
            data_file = Path("data/learning.json")
            if data_file.exists():
                with open(data_file, 'r') as f:
                    self.learned_patterns = json.load(f)
        except Exception as e:
            logger.error(f"Error loading learning data: {str(e)}")

    def _save_learning_data(self):
        """Save learned patterns to file."""
        try:
            data_file = Path("data/learning.json")
            data_file.parent.mkdir(exist_ok=True)
            with open(data_file, 'w') as f:
                json.dump(self.learned_patterns, f)
        except Exception as e:
            logger.error(f"Error saving learning data: {str(e)}")

    def process_text(self, text: str) -> str:
        """Process input text and return appropriate response."""
        try:
            # Check learned patterns first
            for pattern, response in self.learned_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    return response

            # Check built-in rules
            for pattern, response in self.rules.items():
                if re.search(pattern, text, re.IGNORECASE):
                    if callable(response):
                        return response()
                    return response

            # If no match found
            return "I'm not sure how to respond to that. You can teach me by using the /learn command."

        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return "I encountered an error while processing your input."

    def learn_pattern(self, pattern: str, response: str) -> bool:
        """Learn a new pattern and response."""
        try:
            self.learned_patterns[pattern] = response
            self._save_learning_data()
            return True
        except Exception as e:
            logger.error(f"Error learning pattern: {str(e)}")
            return False

class ContextManager:
    def __init__(self, max_context_length: int = 1024):
        self.max_context_length = max_context_length
        self.context: List[Dict[str, str]] = []
        self.memory: Dict[str, any] = {}

    def add_to_context(self, user_input: str, response: str):
        """Add a new interaction to the context."""
        self.context.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.context) > self.max_context_length:
            self.context.pop(0)

    def get_recent_context(self, n: int = 5) -> List[Dict[str, str]]:
        """Get the n most recent interactions."""
        return self.context[-n:]

    def clear_context(self):
        """Clear the conversation context."""
        self.context.clear()

    def save_memory(self, key: str, value: any):
        """Save information to long-term memory."""
        self.memory[key] = value

    def get_memory(self, key: str) -> Optional[any]:
        """Retrieve information from long-term memory."""
        return self.memory.get(key)

    def clear_memory(self):
        """Clear all stored memory."""
        self.memory.clear() 