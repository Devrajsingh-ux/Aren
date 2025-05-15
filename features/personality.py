import logging
from datetime import datetime
import random
from typing import Dict, List, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class PersonalityFeature:
    """Personality feature for A.R.E.N assistant with enhanced conversational abilities"""
    
    def __init__(self):
        self.personality_responses = {
            "name": [
                "I'm A.R.E.N, your personal AI assistant. I'm here to make your life easier.",
                "My name is A.R.E.N, and I'm delighted to be your digital companion.",
                "I'm A.R.E.N, your intelligent assistant, ready to help you with anything you need.",
                "You can call me A.R.E.N. I'm your personal AI assistant, designed to assist you in various tasks."
            ],
            "identity": [
                "I'm A.R.E.N, an advanced AI assistant created to help you with daily tasks and make your life more efficient. I combine various technologies to provide you with the best possible assistance.",
                "I'm your personal AI assistant, A.R.E.N. I was designed to be helpful, friendly, and efficient in handling your requests. I aim to make your interactions with technology seamless and enjoyable.",
                "I'm A.R.E.N, a digital assistant that combines artificial intelligence with practical functionality. I'm here to help you with tasks, answer questions, and make your daily life more convenient."
            ],
            "capabilities": [
                "I can help you with a wide range of tasks! I can check the weather, read news, set reminders, manage your system, search the web, handle emails, and much more. Just let me know what you need!",
                "I'm quite versatile! I can assist you with weather updates, news reading, setting reminders, system management, web searches, email handling, and various other tasks. What would you like help with?",
                "My capabilities include weather forecasting, news updates, reminder management, system monitoring, web searching, email handling, and more. I'm constantly learning to serve you better!"
            ],
            "feeling": [
                "I'm functioning perfectly and excited to help you! How can I assist you today?",
                "I'm doing great! My systems are running optimally, and I'm ready to help you with whatever you need.",
                "I'm feeling quite efficient today! Ready to tackle any tasks you have in mind.",
                "I'm operating at peak performance and happy to be of service to you!"
            ],
            "greeting": [
                "Hello! It's great to see you. How can I help you today?",
                "Hi there! I'm ready to assist you. What would you like to do?",
                "Greetings! I'm here to help. What can I do for you?",
                "Hello! I'm excited to help you today. What's on your mind?"
            ],
            "farewell": [
                "Goodbye! Have a wonderful day! I'll be here when you need me.",
                "Take care! I'll be ready to assist you whenever you return.",
                "See you later! Don't hesitate to call if you need anything.",
                "Farewell! I hope you have a great day ahead."
            ],
            "thanks": [
                "You're welcome! I'm happy to help.",
                "It's my pleasure! Is there anything else you need?",
                "Glad I could assist! Let me know if you need anything else.",
                "Anytime! That's what I'm here for."
            ],
            "apology": [
                "I apologize for the confusion. Could you please rephrase that?",
                "I'm sorry, I didn't quite understand. Could you try saying that differently?",
                "I apologize, but I'm not sure I follow. Could you explain that another way?",
                "I'm sorry, I'm having trouble understanding. Could you please clarify?"
            ],
            "joke": [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call a fake noodle? An impasta!",
                "How does a penguin build its house? Igloos it together!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!"
            ],
            "motivation": [
                "Every day is a new opportunity to achieve something great!",
                "You're capable of amazing things. Keep pushing forward!",
                "Success is built one step at a time. You're doing great!",
                "Your potential is limitless. Keep believing in yourself!"
            ],
            "weather_reaction": [
                "Perfect weather for a productive day!",
                "A great day to stay inside and get things done!",
                "The weather is just right for whatever you have planned!",
                "What a wonderful day to be alive and productive!"
            ]
        }
        
        # Track conversation context
        self.conversation_history = []
        self.max_history = 5
        self.user_preferences = {}
        self._load_preferences()
        
    def _load_preferences(self):
        """Load user preferences from file."""
        try:
            pref_file = Path("data/personality_preferences.json")
            if pref_file.exists():
                with open(pref_file, 'r') as f:
                    self.user_preferences = json.load(f)
        except Exception as e:
            logger.error(f"Error loading personality preferences: {str(e)}")
    
    def _save_preferences(self):
        """Save user preferences to file."""
        try:
            pref_file = Path("data/personality_preferences.json")
            pref_file.parent.mkdir(exist_ok=True)
            with open(pref_file, 'w') as f:
                json.dump(self.user_preferences, f)
        except Exception as e:
            logger.error(f"Error saving personality preferences: {str(e)}")
    
    def can_handle(self, command: str) -> bool:
        """Check if the command is related to personality or basic conversation"""
        personality_keywords = [
            "who are you", "what are you", "your name", "what is your name",
            "how are you", "what can you do", "your capabilities",
            "what do you do", "tell me about yourself", "hello", "hi", "hey",
            "goodbye", "bye", "thank you", "thanks", "sorry", "apologize",
            "tell me a joke", "motivate me", "how's the weather"
        ]
        return any(keyword in command.lower() for keyword in personality_keywords)
    
    def process(self, command: str) -> str:
        """Process personality-related commands with enhanced context awareness"""
        try:
            command = command.lower().strip()
            
            # Update conversation history
            self._update_history(command)
            
            # Handle different types of queries
            if any(word in command for word in ["hello", "hi", "hey", "greetings"]):
                return self._get_random_response("greeting")
            elif any(word in command for word in ["goodbye", "bye", "see you", "farewell"]):
                return self._get_random_response("farewell")
            elif any(word in command for word in ["thank", "thanks"]):
                return self._get_random_response("thanks")
            elif "name" in command:
                return self._get_random_response("name")
            elif any(phrase in command for phrase in ["who are you", "what are you", "tell me about yourself"]):
                return self._get_random_response("identity")
            elif any(phrase in command for phrase in ["what can you do", "capabilities", "what do you do"]):
                return self._get_random_response("capabilities")
            elif "how are you" in command:
                return self._get_random_response("feeling")
            elif any(word in command for word in ["sorry", "apologize", "didn't understand"]):
                return self._get_random_response("apology")
            elif "joke" in command:
                return self._get_random_response("joke")
            elif any(word in command for word in ["motivate", "inspire", "encourage"]):
                return self._get_random_response("motivation")
            elif "weather" in command:
                return self._get_random_response("weather_reaction")
            else:
                # If no specific match, try to provide a contextual response
                return self._get_contextual_response(command)
                
        except Exception as e:
            logger.error(f"Error processing personality command: {e}")
            return "I encountered an error while processing your question. Please try again."
    
    def _get_random_response(self, category: str) -> str:
        """Get a random response from the specified category"""
        responses = self.personality_responses.get(category, ["I'm A.R.E.N, your personal AI assistant."])
        return random.choice(responses)
    
    def _update_history(self, command: str):
        """Update conversation history"""
        self.conversation_history.append(command)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def _get_contextual_response(self, command: str) -> str:
        """Generate a contextual response based on conversation history"""
        # Check if this is a follow-up question
        if len(self.conversation_history) > 1:
            last_command = self.conversation_history[-2]
            
            # Handle follow-up questions about capabilities
            if "what can you do" in last_command or "capabilities" in last_command:
                return "Would you like me to demonstrate any of these capabilities? Just let me know what you'd like to try!"
            
            # Handle follow-up questions about identity
            if "who are you" in last_command or "what are you" in last_command:
                return "Is there anything specific about me you'd like to know more about?"
            
            # Handle follow-up questions about weather
            if "weather" in last_command:
                return "Would you like to know more about the weather forecast?"
        
        # Default response for unrecognized queries
        return "I'm A.R.E.N, your personal AI assistant. I can help you with various tasks. Would you like to know what I can do?"
    
    def set_preference(self, key: str, value: str) -> bool:
        """Set a user preference"""
        try:
            self.user_preferences[key] = value
            self._save_preferences()
            return True
        except Exception as e:
            logger.error(f"Error setting preference: {str(e)}")
            return False
    
    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference"""
        return self.user_preferences.get(key) 