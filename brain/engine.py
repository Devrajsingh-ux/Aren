"""
AREN Engine - Core decision-making integration
This module integrates the decision making system with AREN's existing capabilities.
"""

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

class ArenEngine:
    def __init__(self):
        self.decision_maker = DecisionMaker()
        self.context_manager = ContextManager()
        logger.info("AREN Engine initialized")
        
        # Define capability handlers
        self.capabilities = {
            'time': self._handle_time,
            'date': self._handle_date,
            'search': web_search,
            'launch_app': launch_application,
            'greeting': get_greeting,
            'joke': get_joke,
            'identity': get_identity,
            'weather': self._handle_weather,
            'calculation': self._handle_calculation,
            'translate': self._handle_translation,
            'unknown': self._handle_unknown
        }
    
    def process_input(self, user_input):
        """
        Main input processing function - decides what to do with user input
        and returns a response
        """
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
        
        # Get handler for the selected capability
        handler = self.capabilities.get(selected_capability, self.capabilities['unknown'])
        
        # Execute the handler with appropriate arguments
        if selected_capability == 'weather':
            location = extract_location(user_input)
            response = handler(location)
        elif selected_capability == 'calculation':
            expression = extract_calculation(user_input)
            response = handler(expression)
        elif selected_capability == 'translate':
            text, target_lang, source_lang = extract_translation_request(user_input)
            response = handler(text, target_lang, source_lang)
        elif selected_capability in ['time', 'date', 'unknown', 'greeting', 'joke', 'identity']:
            response = handler()
        else:
            response = handler(user_input)
        
        # Record this interaction in context
        self.context_manager.update_conversation(user_input, response)
        self.context_manager.add_action('capability_used', {
            'capability': selected_capability,
            'confidence': confidence,
            'reasoning': reasoning
        })
        
        return response
    
    def _identify_capabilities(self, user_input):
        """Identify which capabilities might be applicable to the input"""
        user_input_lower = user_input.lower()
        
        capabilities = []
        
        # Identity detection - MUST be checked BEFORE search detection to prevent confusion
        # These are exact patterns that should match identity questions
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
                # Important: Return immediately to avoid treating as a search query
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
        # Also check for direct calculation patterns like "2+2"
        has_calc_operator = any(op in user_input for op in ["+", "-", "*", "/", "÷", "×"])
        
        if any(trigger in user_input_lower for trigger in calc_triggers) or has_calc_operator:
            # Confirm with the extraction function
            if extract_calculation(user_input):
                capabilities.append('calculation')
                
        # Translation detection
        translation_triggers = ["translate", "translation", "meaning", "anuvad", "meaning of", "in english", "in hindi"]
        if any(trigger in user_input_lower for trigger in translation_triggers):
            # Confirm with the extraction function
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
    
    def _handle_time(self):
        """Handle time requests"""
        return f"The current time is {get_current_time()}"
    
    def _handle_date(self):
        """Handle date requests"""
        return f"Today's date is {get_current_date()}"
    
    def _handle_weather(self, location=None):
        """Handle weather requests"""
        return get_weather(location)
    
    def _handle_calculation(self, expression=None):
        """Handle calculation requests"""
        if not expression:
            return "I need an expression to calculate. (Mujhe ganana ke liye kuch dein.)"
        return calculate(expression)
    
    def _handle_translation(self, text=None, target_lang=None, source_lang=None):
        """Handle translation requests"""
        if not text or not target_lang:
            return "I need text and a target language to translate. (Anuvad ke liye text aur bhasha chahiye.)"
        return translate_text(text, target_lang, source_lang)
    
    def _handle_unknown(self):
        """Handle unknown requests"""
        return "I'm not sure how to help with that yet. (Main samajh nahi paaya, dobara poochhein!)" 