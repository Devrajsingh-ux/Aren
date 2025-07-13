"""
Context management system for AREN
This module manages and provides context for AREN's decision making process.
"""

from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Optional, Any
from utils.logging_utils import logger
from utils.database import db_manager
from features.information.time_date import get_time_of_day

class ContextManager:
    def __init__(self, memory_dir=None, device_id=None):
        # Directory to store user preferences
        self.memory_dir = memory_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory', 'user_data')
        
        # Ensure memory directory exists
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
            logger.info(f"Created memory directory: {self.memory_dir}")
        
        # Initialize or get user
        self.device_id = device_id or os.getenv('DEVICE_ID', 'default_device')
        self.user_id = db_manager.get_or_create_user(self.device_id)
            
        self.contexts = {
            'user_preferences': self._load_user_preferences(),
            'current_conversation': [],
            'environment': self._get_environment_context(),
            'recent_actions': [],
            'session_start_time': datetime.now(),
            'conversation_history': [],
            'active_tasks': [],
            'recent_memories': []
        }
        
        # Load recent data from database
        self._load_recent_data()
        
        logger.info("Context Manager initialized")
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences from memory file"""
        try:
            preferences_file = os.path.join(self.memory_dir, f'user_preferences_{self.device_id}.json')
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    logger.info("User preferences loaded successfully")
                    return prefs
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
        return {}
    
    def _save_user_preferences(self) -> None:
        """Save user preferences to memory file"""
        try:
            preferences_file = os.path.join(self.memory_dir, f'user_preferences_{self.device_id}.json')
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.contexts['user_preferences'], f, indent=2, ensure_ascii=False)
            logger.info("User preferences saved successfully")
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
    
    def _get_environment_context(self) -> Dict[str, Any]:
        """Get current environment context"""
        return {
            'time_of_day': get_time_of_day(),
            'timestamp': datetime.now().isoformat(),
            'device_id': self.device_id,
            'user_id': self.user_id
        }
    
    def _load_recent_data(self) -> None:
        """Load recent conversations, tasks, and memories from database"""
        try:
            # Load recent conversations
            responses = db_manager.get_responses_for_prompt("", self.user_id, limit=10)
            self.contexts['conversation_history'] = [
                {'prompt': resp.prompt.text, 'response': resp.text, 'language': resp.language}
                for resp in responses
            ]
            
            # Load active tasks
            tasks = db_manager.get_pending_tasks(self.user_id)
            self.contexts['active_tasks'] = [
                {
                    'task': task.task,
                    'priority': task.priority,
                    'due_date': task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ]
            
            # Load recent memories
            memories = db_manager.get_memories(self.user_id)
            self.contexts['recent_memories'] = [
                {'note': memory.note, 'context': memory.context}
                for memory in memories
            ]
            
            logger.info("Recent data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading recent data: {e}")
    
    def update_conversation(self, user_input: str, response: str, language: str = "en") -> None:
        """Update conversation history with new exchange"""
        try:
            # Add to current conversation
            exchange = {
                'user_input': user_input,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'language': language
            }
            self.contexts['current_conversation'].append(exchange)
            
            # Save to database
            db_manager.save_conversation(
                user_id=self.user_id,
                prompt_text=user_input,
                response_text=response,
                language=language
            )
            
            # Update conversation history
            self.contexts['conversation_history'].insert(0, {
                'prompt': user_input,
                'response': response,
                'language': language
            })
            
            # Trim history if too long
            if len(self.contexts['conversation_history']) > 20:
                self.contexts['conversation_history'] = self.contexts['conversation_history'][:20]
                
            logger.info("Added conversation exchange: %s...", user_input[:50])
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
    
    def add_memory(self, note: str, context: str, expires_at: Optional[datetime] = None) -> None:
        """Add a memory note"""
        try:
            # Save to database
            db_manager.add_memory(
                user_id=self.user_id,
                note=note,
                context=context,
                expires_at=expires_at
            )
            
            # Update local context
            self.contexts['recent_memories'].insert(0, {
                'note': note,
                'context': context
            })
            
            # Trim if too many memories
            if len(self.contexts['recent_memories']) > 50:
                self.contexts['recent_memories'] = self.contexts['recent_memories'][:50]
                
            logger.info("Added memory: %s", note[:50])
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
    
    def add_task(self, task: str, priority: int = 1, due_date: Optional[datetime] = None) -> None:
        """Add a task"""
        try:
            # Save to database
            db_manager.add_task(
                user_id=self.user_id,
                task=task,
                due_date=due_date or datetime.now() + timedelta(days=1),
                priority=priority
            )
            
            # Update local context
            self.contexts['active_tasks'].append({
                'task': task,
                'priority': priority,
                'due_date': due_date.isoformat() if due_date else None
            })
            
            logger.info("Added task: %s", task[:50])
        except Exception as e:
            logger.error(f"Error adding task: {e}")
    
    def add_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Record an action in the context"""
        try:
            action = {
                'type': action_type,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            self.contexts['recent_actions'].append(action)
            
            # Keep only recent actions
            if len(self.contexts['recent_actions']) > 20:
                self.contexts['recent_actions'] = self.contexts['recent_actions'][-20:]
                
            logger.info("Added action: %s", action_type)
        except Exception as e:
            logger.error(f"Error adding action: {e}")
    
    def update_user_preference(self, key: str, value: Any) -> None:
        """Update a user preference"""
        try:
            self.contexts['user_preferences'][key] = value
            self._save_user_preferences()
            logger.info("Updated user preference: %s", key)
        except Exception as e:
            logger.error(f"Error updating user preference: {e}")
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get the complete context for decision making"""
        return {
            'user': {
                'id': self.user_id,
                'device_id': self.device_id,
                'preferences': self.contexts['user_preferences']
            },
            'conversation': {
                'current': self.contexts['current_conversation'][-5:] if self.contexts['current_conversation'] else [],
                'history': self.contexts['conversation_history'][:10]
            },
            'environment': self._get_environment_context(),
            'memory': {
                'recent': self.contexts['recent_memories'][:5],
                'tasks': self.contexts['active_tasks']
            },
            'session': {
                'start_time': self.contexts['session_start_time'].isoformat(),
                'recent_actions': self.contexts['recent_actions'][-5:]
            }
        }
    
    def get_keywords_from_input(self, user_input: str) -> List[str]:
        """Extract keywords from user input for context"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = user_input.lower().split()
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were'}
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        return keywords[:10]  # Return top 10 keywords 