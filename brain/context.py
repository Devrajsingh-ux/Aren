"""
Context management system for AREN
This module manages and provides context for AREN's decision making process.
"""

from datetime import datetime
import os
import json
from utils.logging_utils import logger
from features.information.time_date import get_time_of_day

class ContextManager:
    def __init__(self, memory_dir=None):
        # Directory to store user preferences and context history
        self.memory_dir = memory_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory', 'user_data')
        
        # Ensure memory directory exists
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
            logger.info(f"Created memory directory: {self.memory_dir}")
            
        self.contexts = {
            'user_preferences': self._load_user_preferences(),
            'current_conversation': [],
            'environment': self._get_environment_context(),
            'recent_actions': [],
            'session_start_time': datetime.now()
        }
        
        logger.info("Context Manager initialized")
        
    def _load_user_preferences(self):
        """Load user preferences from memory file"""
        try:
            preferences_file = os.path.join(self.memory_dir, 'user_preferences.json')
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r') as f:
                    prefs = json.load(f)
                    logger.info("User preferences loaded successfully")
                    return prefs
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
        return {}
        
    def _save_user_preferences(self):
        """Save user preferences to memory file"""
        try:
            preferences_file = os.path.join(self.memory_dir, 'user_preferences.json')
            with open(preferences_file, 'w') as f:
                json.dump(self.contexts['user_preferences'], f, indent=2)
            logger.info("User preferences saved successfully")
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
    
    def _get_environment_context(self):
        """Get context about the current environment"""
        return {
            'platform': os.name,
            'time_of_day': get_time_of_day(),
            'is_weekend': datetime.now().weekday() >= 5
        }
        
    def update_conversation(self, user_input, system_response):
        """Add a conversation exchange to the context"""
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'system_response': system_response
        }
        self.contexts['current_conversation'].append(exchange)
        
        # Limit conversation history to last 10 exchanges
        if len(self.contexts['current_conversation']) > 10:
            self.contexts['current_conversation'] = self.contexts['current_conversation'][-10:]
            
        logger.info(f"Added conversation exchange: {user_input[:30]}...")
            
    def add_action(self, action_type, action_details):
        """Record an action that was performed"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'details': action_details
        }
        self.contexts['recent_actions'].append(action)
        
        # Limit action history to last 20 actions
        if len(self.contexts['recent_actions']) > 20:
            self.contexts['recent_actions'] = self.contexts['recent_actions'][-20:]
            
        logger.info(f"Added action: {action_type}")
    
    def update_user_preference(self, category, preference_key, preference_value):
        """Update a user preference"""
        if category not in self.contexts['user_preferences']:
            self.contexts['user_preferences'][category] = {}
            
        self.contexts['user_preferences'][category][preference_key] = preference_value
        self._save_user_preferences()
        logger.info(f"Updated user preference: {category}.{preference_key}")
    
    def get_full_context(self):
        """Get the complete context dictionary"""
        # Update dynamic environment context 
        self.contexts['environment'] = self._get_environment_context()
        return self.contexts
        
    def get_keywords_from_input(self, user_input):
        """Extract potential keywords from user input"""
        # Simple keyword extraction - could be enhanced with NLP
        words = user_input.lower().split()
        # Filter out common words (simple stopwords)
        stopwords = {'a', 'an', 'the', 'to', 'and', 'or', 'but', 'in', 'on', 'at', 'with', 'by'}
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        return keywords 