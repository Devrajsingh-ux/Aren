"""
AREN Engine - Core decision-making integration
This module integrates the decision making system with AREN's existing capabilities.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import traceback

from features.information.search import web_search
from features.information.time_date import get_current_time, get_current_date
from features.information.weather import get_weather, extract_location
from features.information.calculator import calculate, extract_calculation
from features.information.translator import translate_text, extract_translation_request
from features.actions.automation import launch_application
from features.interaction.personality import get_greeting, get_joke, get_identity
from brain.decision import DecisionMaker
from brain.context import ContextManager
from utils.logging_utils import logger
from utils.database import db_manager

class ArenEngine:
    def __init__(self):
        self.decision_maker = DecisionMaker()
        self.context_manager = ContextManager()
        
        # Initialize creator information if not exists
        self._initialize_creator_info()
        
        # Define capability handlers with their requirements
        self.capabilities = {
            'time': {
                'handler': self._handle_time,
                'requires_args': False,
                'description': 'Get current time'
            },
            'date': {
                'handler': self._handle_date,
                'requires_args': False,
                'description': 'Get current date'
            },
            'search': {
                'handler': web_search,
                'requires_args': True,
                'description': 'Search the web for information'
            },
            'launch_app': {
                'handler': launch_application,
                'requires_args': True,
                'description': 'Launch applications'
            },
            'greeting': {
                'handler': get_greeting,
                'requires_args': False,
                'description': 'Respond to greetings'
            },
            'joke': {
                'handler': get_joke,
                'requires_args': False,
                'description': 'Tell jokes'
            },
            'identity': {
                'handler': self._handle_identity,
                'requires_args': False,
                'description': 'Provide identity information'
            },
            'weather': {
                'handler': self._handle_weather,
                'requires_args': True,
                'description': 'Get weather information'
            },
            'calculation': {
                'handler': self._handle_calculation,
                'requires_args': True,
                'description': 'Perform calculations'
            },
            'translate': {
                'handler': self._handle_translation,
                'requires_args': True,
                'description': 'Translate text'
            },
            'unknown': {
                'handler': self._handle_unknown,
                'requires_args': False,
                'description': 'Handle unknown requests'
            }
        }
        
        logger.info("AREN Engine initialized")
    
    def process_input(self, user_input: str) -> str:
        """
        Main input processing function - decides what to do with user input
        and returns a response
        """
        try:
            logger.info(f"Processing user input: {user_input}")
            
            # Extract keywords for context
            keywords = self.context_manager.get_keywords_from_input(user_input)
            
            # Identify possible capabilities to use
            capability_options = self._identify_capabilities(user_input)
            
            if not capability_options:
                capability_options = ['unknown']
                
            # Prepare context for decision making
            context = {
                'user_input': user_input,
                'keywords': keywords,
                'input_lower': user_input.lower(),
                'historical': self.context_manager.get_full_context()
            }
            
            # Make decision on which capability to use
            selected_capability, confidence, reasoning = self.decision_maker.make_decision(
                capability_options, 
                context=context
            )
            
            logger.info(f"Selected capability: {selected_capability} with confidence: {confidence}")
            
            # Get handler configuration for the selected capability
            handler_config = self.capabilities.get(selected_capability)
            if not handler_config:
                logger.error(f"No handler found for capability: {selected_capability}")
                return self._handle_unknown()
            
            handler = handler_config['handler']
            requires_args = handler_config['requires_args']
            
            # Execute the handler with appropriate arguments
            try:
                if selected_capability == 'weather':
                    location = extract_location(user_input)
                    response = handler(location)
                elif selected_capability == 'calculation':
                    expression = extract_calculation(user_input)
                    response = handler(expression)
                elif selected_capability == 'translate':
                    text, target_lang, source_lang = extract_translation_request(user_input)
                    response = handler(text, target_lang, source_lang)
                elif requires_args:
                    response = handler(user_input)
                else:
                    response = handler()
            except Exception as e:
                logger.error(f"Error executing handler for {selected_capability}: {str(e)}")
                logger.debug(f"Handler error details: {traceback.format_exc()}")
                response = self._handle_error(selected_capability, str(e))
            
            # Record this interaction in context
            self.context_manager.update_conversation(
                user_input=user_input,
                response=response,
                language=self._detect_language(response)
            )
            
            self.context_manager.add_action('capability_used', {
                'capability': selected_capability,
                'confidence': confidence,
                'reasoning': reasoning,
                'success': True
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in main processing loop: {str(e)}")
            logger.debug(f"Processing error details: {traceback.format_exc()}")
            return "I encountered an error. Please try again. (Kuch gadbad ho gayi. Phir se koshish karein.)"
    
    def _identify_capabilities(self, user_input: str) -> List[str]:
        """Identify which capabilities might be applicable to the input"""
        user_input_lower = user_input.lower()
        capabilities = []
        
        # Identity detection - MUST be checked BEFORE search detection
        identity_triggers = [
            "who are you", "tum kaun ho", "what is your name", "what's your name", 
            "naam kya hai", "about yourself", "introduce yourself", 
            "tell me about you", "tell me about yourself", "apne baare mein batao",
            "what are you", "who made you", "what do you do"
        ]
        
        # Check for identity first with exact matching
        for trigger in identity_triggers:
            if trigger in user_input_lower:
                capabilities.append('identity')
                return capabilities
        
        # Time detection
        if any(x in user_input_lower for x in ["time", "samay", "kitna baj gaya", "what's the time"]):
            capabilities.append('time')
            
        # Date detection
        if any(x in user_input_lower for x in ["date", "aaj ki tareekh", "today's date", "what's the date"]):
            capabilities.append('date')
        
        # Weather detection
        weather_triggers = ["weather", "temperature", "forecast", "mausam", "garmi", "sardi", "rainy", "sunny", "climate"]
        if any(trigger in user_input_lower for trigger in weather_triggers):
            capabilities.append('weather')
            
        # Calculation detection
        calc_triggers = ["calculate", "compute", "sum", "add", "subtract", "multiply", "divide", "equals", "equal to", "="]
        has_calc_operator = any(op in user_input for op in ["+", "-", "*", "/", "÷", "×"])
        
        if any(trigger in user_input_lower for trigger in calc_triggers) or has_calc_operator:
            if extract_calculation(user_input):
                capabilities.append('calculation')
                
        # Translation detection
        translation_triggers = ["translate", "translation", "meaning", "anuvad", "meaning of", "in english", "in hindi"]
        if any(trigger in user_input_lower for trigger in translation_triggers):
            if extract_translation_request(user_input) != (None, None, None):
                capabilities.append('translate')
            
        # Application launching detection
        app_triggers = ["open ", "launch ", "start ", "khol", "chalu karo", "shuru karo"]
        if any(trigger in user_input_lower for trigger in app_triggers):
            capabilities.append('launch_app')
            
        # Greeting detection
        greeting_triggers = ["hello", "hi", "namaste", "hey", "salaam", "pranam"]
        if any(trigger in user_input_lower for trigger in greeting_triggers):
            capabilities.append('greeting')
            
        # Joke detection
        joke_triggers = ["joke", "mazaak", "funny", "kuch funny bolo", "kuch mazaak batao"]
        if any(trigger in user_input_lower for trigger in joke_triggers):
            capabilities.append('joke')
            
        # Web search detection - AFTER checking for specific capabilities
        search_triggers = [
            "search ", "look up ", 
            "who is ", "what is ", "when is ", "where is ", "why is ", 
            "who was ", "what was ", "when was ", "where was ", "why was ",
            "who are ", "what are ", "when are ", "where are ", "why are ",
            "who built ", "who created ", "who made ", "who discovered ",
            "who build ", "who create ", "who make ", "who discover ",
            "how do", "how to", "how can", "how does", "how did",
            "tell me about ", "information on ", "details about ",
            "kya hai", "kaun hai", "kab hai", "kahan hai", "kyun hai",
            "kisne banaya", "kaise bana", "kab bana", "batao"
        ]
        if any(user_input_lower.startswith(trigger) or trigger in user_input_lower for trigger in search_triggers):
            capabilities.append('search')
        
        # Check for general question patterns
        if user_input_lower.startswith(("who", "what", "when", "where", "why", "how")) or "?" in user_input:
            capabilities.append('search')
            
        return capabilities
    
    def _handle_time(self) -> str:
        """Handle time requests"""
        return f"The current time is {get_current_time()}"
    
    def _handle_date(self) -> str:
        """Handle date requests"""
        return f"Today's date is {get_current_date()}"
    
    def _handle_weather(self, location: Optional[str] = None) -> str:
        """Handle weather requests"""
        if not location:
            return "I need a location to check the weather. (Mausam jaanne ke liye jagah ka naam batayein.)"
        return get_weather(location)
    
    def _handle_calculation(self, expression: Optional[str] = None) -> str:
        """Handle calculation requests"""
        if not expression:
            return "I need an expression to calculate. (Mujhe ganana ke liye kuch dein.)"
        return calculate(expression)
    
    def _handle_translation(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        """Handle translation requests"""
        if not text or not target_lang:
            return "I need text and target language for translation. (Anuvad ke liye text aur bhasha batayein.)"
        return translate_text(text, target_lang, source_lang)
    
    def _handle_identity(self) -> str:
        """Handle identity requests with creator information"""
        try:
            info = db_manager.get_system_info(category='creator')
            if not info:
                return "I am AREN, your AI assistant."
            
            creator_info = {item['key']: item['value'] for item in info}
            
            response = (
                f"I am {creator_info.get('system_name', 'AREN')}, "
                f"created by {creator_info.get('creator_name', 'Devraj Singh Shakya')} "
                f"(known as {creator_info.get('creator_alias', 'Ghost')}, "
                f"nickname: {creator_info.get('creator_nickname', 'Dev')}). "
                f"I was created on {creator_info.get('creation_date', 'February 1st, 2025')}. "
                f"My creator is {creator_info.get('creator_education', 'a B.Tech CSE student')}. "
                "I'm here to assist you with various tasks!"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling identity: {e}")
            return "I am AREN, your AI assistant. (I apologize, but I'm having trouble accessing my detailed information right now.)"
    
    def _handle_unknown(self) -> str:
        """Handle unknown requests"""
        return "I'm not sure how to help with that. Could you please rephrase or try something else? (Mujhe samajh nahi aaya. Kripya doosre tarike se batayen.)"
    
    def _handle_error(self, capability: str, error: str) -> str:
        """Handle errors in capability execution"""
        error_responses = {
            'weather': "Sorry, I couldn't get the weather information right now. (Mausam ki jaankari abhi uplabdh nahi hai.)",
            'calculation': "Sorry, I couldn't perform that calculation. Please check the format. (Ganana nahi kar paya. Format check karein.)",
            'translate': "Sorry, I couldn't translate that. Please try again. (Anuvad nahi kar paya. Dobara koshish karein.)",
            'launch_app': "Sorry, I couldn't launch that application. (App shuru nahi kar paya.)",
            'search': "Sorry, I couldn't find that information. (Jaankari nahi mil payi.)"
        }
        return error_responses.get(capability, "Sorry, something went wrong. Please try again. (Kuch gadbad ho gayi. Dobara koshish karein.)")
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character sets"""
        # This is a basic implementation - could be enhanced with proper language detection
        devanagari = any('\u0900' <= c <= '\u097F' for c in text)
        return 'hi' if devanagari else 'en' 

    def _initialize_creator_info(self):
        """Initialize creator information in database"""
        try:
            creator_info = {
                'creator_name': 'Devraj Singh Shakya',
                'creator_nickname': 'Dev',
                'creator_alias': 'Ghost',
                'creator_education': 'B.Tech CSE student at Amity University Gwalior (joined 2024)',
                'creation_date': '2025-02-01',
                'system_name': 'AREN (Assistant for Regular and Extraordinary Needs)'
            }
            
            for key, value in creator_info.items():
                db_manager.add_system_info(key, value, category='creator')
                
        except Exception as e:
            logger.error(f"Error initializing creator info: {e}") 