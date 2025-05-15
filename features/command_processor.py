import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import webbrowser
import subprocess
from pathlib import Path
import json
from .web_search import WebSearcher
from .app_launcher import app_launcher
from .personality import PersonalityFeature

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        self.commands = {
            'time': self._get_time,
            'date': self._get_date,
            'weather': self._get_weather,
            'reminder': self._handle_reminder,
            'open': self._open_application,
            'search': self._web_search,
            'learn': self._handle_learning,
            'help': self._show_help,
            'info': self._get_info
        }
        self.reminders = []
        self.learning_data = {}
        self.web_searcher = WebSearcher()
        self.personality = PersonalityFeature()
        self._load_data()

    def _load_data(self):
        """Load saved data from files."""
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Load reminders
            reminder_file = data_dir / "reminders.json"
            if reminder_file.exists():
                with open(reminder_file, 'r') as f:
                    self.reminders = json.load(f)
            
            # Load learning data
            learning_file = data_dir / "learning.json"
            if learning_file.exists():
                with open(learning_file, 'r') as f:
                    self.learning_data = json.load(f)
                    
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")

    def _save_data(self):
        """Save data to files."""
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Save reminders
            with open(data_dir / "reminders.json", 'w') as f:
                json.dump(self.reminders, f)
            
            # Save learning data
            with open(data_dir / "learning.json", 'w') as f:
                json.dump(self.learning_data, f)
                
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

    def process_command(self, command: str, args: List[str]) -> str:
        """Process a command and its arguments."""
        try:
            # Check if it's a personality-related command first
            if self.personality.can_handle(command):
                return self.personality.process(command)
            
            # Special handling for "open" command
            if command.lower() == "open" and args:
                return self._open_application(args[0])
            
            if command in self.commands:
                return self.commands[command](*args)
            else:
                return f"Unknown command: {command}. Type 'help' for available commands."
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return "An error occurred while processing your command."

    def _get_time(self) -> str:
        """Get current time."""
        return datetime.now().strftime("%I:%M %p")

    def _get_date(self) -> str:
        """Get current date."""
        return datetime.now().strftime("%A, %B %d, %Y")

    def _get_weather(self, location: str = "current") -> str:
        """Get weather information for a location."""
        # This is a placeholder. In a real implementation, you would integrate with a weather API
        return f"Weather information for {location} is not available in this version."

    def _handle_reminder(self, action: str, *args) -> str:
        """Handle reminder-related commands."""
        if action == "add":
            if len(args) < 2:
                return "Please provide a reminder text and time."
            reminder_text = args[0]
            reminder_time = args[1]
            self.reminders.append({
                "text": reminder_text,
                "time": reminder_time,
                "created": datetime.now().isoformat()
            })
            self._save_data()
            return f"Reminder set for {reminder_time}: {reminder_text}"
        
        elif action == "list":
            if not self.reminders:
                return "No reminders set."
            return "\n".join([f"{i+1}. {r['text']} at {r['time']}" 
                            for i, r in enumerate(self.reminders)])
        
        elif action == "delete":
            try:
                index = int(args[0]) - 1
                if 0 <= index < len(self.reminders):
                    reminder = self.reminders.pop(index)
                    self._save_data()
                    return f"Removed reminder: {reminder['text']}"
                else:
                    return "Invalid reminder index."
            except ValueError:
                return "Please provide a valid reminder number."
        
        return "Invalid reminder action. Use 'add', 'list', or 'delete'."

    def _open_application(self, app_name: str) -> str:
        """Open a specified application using the AppLauncher."""
        if not app_name:
            return "Please specify an application to open."
        success, message = app_launcher.launch_application(app_name)
        return message

    def _web_search(self, query: str) -> str:
        """Perform a web search and open the results."""
        try:
            # Remove common search phrases
            query = query.lower()
            for phrase in ['search', 'find', 'look up', 'browse']:
                query = query.replace(phrase, '').strip()
            
            # Don't process if it's an application opening request
            if query.lower() in app_launcher.get_installed_apps():
                return self._open_application(query)
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching for: {query}"
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return "Failed to perform web search."

    def _get_info(self, query: str) -> str:
        """Get information about a topic or person without opening webpages."""
        try:
            # Remove common information request phrases
            query = query.lower()
            for phrase in ['who is', 'tell me about', 'information about', 'what is', 'who are']:
                query = query.replace(phrase, '').strip()
            
            # First try Wikipedia for a summary
            wiki_summary = self.web_searcher.get_wikipedia_summary(query)
            if wiki_summary:
                # Get search results without opening webpage
                summary, _ = self.web_searcher.search_and_summarize(query)
                
                # Combine Wikipedia summary with search results
                response = f"Wikipedia Summary:\n{wiki_summary}\n\nAdditional Information:\n{summary}"
                return response
            
            # If no Wikipedia summary, just get search results
            summary, _ = self.web_searcher.search_and_summarize(query)
            return summary
            
        except Exception as e:
            logger.error(f"Error getting information: {str(e)}")
            return "Sorry, I encountered an error while getting information."

    def _handle_learning(self, action: str, *args) -> str:
        """Handle learning-related commands."""
        if action == "add":
            if len(args) < 2:
                return "Please provide a topic and information."
            topic = args[0]
            info = " ".join(args[1:])
            self.learning_data[topic] = info
            self._save_data()
            return f"Learned about {topic}."
        
        elif action == "get":
            if not args:
                return "Please provide a topic."
            topic = args[0]
            if topic in self.learning_data:
                return f"{topic}: {self.learning_data[topic]}"
            return f"No information found for {topic}."
        
        elif action == "list":
            if not self.learning_data:
                return "No topics learned yet."
            return "\n".join([f"- {topic}" for topic in self.learning_data.keys()])
        
        return "Invalid learning action. Use 'add', 'get', or 'list'."

    def _show_help(self) -> str:
        """Show available commands and their usage."""
        help_text = """
You can interact with me naturally! Here are some examples:

For Information:
- "Who is [person]?"
- "Tell me about [topic]"
- "What is [subject]?"
- "Information about [topic]"

For Web Search:
- "Search [query]"
- "Open [topic]"
- "Find [information]"
- "Look up [subject]"

For Personality:
- "Tell me about yourself"
- "What can you do?"
- "How are you?"
- "Tell me a joke"
- "Motivate me"
- "How's the weather?"

Other Commands:
- "What time is it?"
- "What's the date?"
- "Help"
- "Set reminder [text] [time]"
- "List reminders"
- "Delete reminder [number]"
- "Open [application]"

You can also teach me new things using:
- "Learn [topic] [information]"
- "What do you know about [topic]?"
- "List learned topics"
"""
        return help_text 