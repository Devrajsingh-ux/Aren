"""
Response generation and management for AREN
This module handles the generation and formatting of AREN's responses
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Union
from utils.logging_utils import logger
from utils.database import db_manager

class ResponseGenerator:
    def __init__(self):
        # Generic responses for different scenarios
        self.error_responses = {
            'general': [
                "I encountered an error. Please try again. (Kuch gadbad ho gayi. Phir se koshish karein.)",
                "Something went wrong. Let's try that again. (Kuch galat ho gaya. Dobara koshish karein.)",
                "Oops! That didn't work as expected. (Oops! Kuch gadbad ho gayi.)"
            ],
            'not_understood': [
                "I'm not sure I understood that. Could you rephrase? (Mujhe samajh nahi aaya. Kya aap dobara keh sakte hain?)",
                "I didn't quite catch that. Can you say it differently? (Main samajh nahi paya. Kya aap alag tarike se keh sakte hain?)",
                "Could you explain that in a different way? (Kya aap ise alag tarike se samjha sakte hain?)"
            ],
            'feature_unavailable': [
                "I can't do that yet, but I'm learning! (Main abhi yeh nahi kar sakta, lekin seekh raha hoon!)",
                "That feature isn't available right now. (Yeh suvidha abhi uplabdh nahi hai.)",
                "I haven't learned how to do that yet. (Main abhi yeh karna nahi seekha hoon.)"
            ],
            'permission_denied': [
                "I don't have permission to do that. (Mujhe yeh karne ki anumati nahi hai.)",
                "Sorry, I'm not allowed to do that. (Maaf kijiye, mujhe yeh karne ki ijazat nahi hai.)",
                "I can't perform that action due to security restrictions. (Suraksha karanon se main yeh nahi kar sakta.)"
            ]
        }

        # Success responses
        self.success_responses = {
            'task_complete': [
                "Done! (Ho gaya!)",
                "Task completed successfully! (Kaam safaltapurvak pura ho gaya!)",
                "All done! What else can I help you with? (Ho gaya! Aur kya madad kar sakta hoon?)"
            ],
            'confirmation': [
                "Sure, I can help with that! (Haan, main isme madad kar sakta hoon!)",
                "I'll take care of that for you! (Main iska dhyan rakhta hoon!)",
                "Let me help you with that! (Main aapki madad karta hoon!)"
            ]
        }

        # Farewell responses
        self.farewell_responses = [
            "Goodbye! Have a great day! (Alvida! Aapka din shubh ho!)",
            "See you later! Take care! (Phir milenge! Dhyan rakhna!)",
            "Bye! Hope to chat with you again soon! (Bye! Jald hi phir baat karenge!)"
        ]

        # Clarification responses
        self.clarification_responses = [
            "Could you provide more details? (Kya aap aur jankari de sakte hain?)",
            "I need more information to help you. (Mujhe aapki madad karne ke liye aur jankari chahiye.)",
            "Could you be more specific? (Kya aap thoda aur spasht kar sakte hain?)"
        ]

    def get_error_response(self, error_type: str = 'general') -> str:
        """Get a random error response of the specified type"""
        responses = self.error_responses.get(error_type, self.error_responses['general'])
        return random.choice(responses)

    def get_success_response(self, success_type: str = 'task_complete') -> str:
        """Get a random success response of the specified type"""
        responses = self.success_responses.get(success_type, self.success_responses['task_complete'])
        return random.choice(responses)

    def get_farewell_response(self) -> str:
        """Get a random farewell response"""
        return random.choice(self.farewell_responses)

    def get_clarification_response(self) -> str:
        """Get a random clarification response"""
        return random.choice(self.clarification_responses)

    def format_response(self, response_text: str, include_timestamp: bool = False) -> str:
        """Format the response with optional timestamp"""
        if include_timestamp:
            timestamp = datetime.now().strftime("%H:%M")
            return f"[{timestamp}] {response_text}"
        return response_text

    def get_contextual_response(self, context: Dict[str, any]) -> str:
        """Generate a response based on conversation context"""
        try:
            # Get responses from database if available
            if 'prompt' in context:
                db_responses = db_manager.get_responses_for_prompt(
                    context['prompt'],
                    context.get('user_id', 'default'),
                    limit=5
                )
                if db_responses:
                    # Select a response considering usage frequency
                    response = self._select_response_from_db(db_responses)
                    if response:
                        return response.text

            # Fall back to generated response if no database match
            return self._generate_fallback_response(context)

        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            return self.get_error_response()

    def _select_response_from_db(self, responses: List[any]) -> Optional[any]:
        """Select a response from database results considering usage patterns"""
        if not responses:
            return None

        # Simple weighted random selection based on inverse of usage count
        total_uses = sum(r.used_count for r in responses)
        weights = [(total_uses - r.used_count + 1) for r in responses]
        total_weight = sum(weights)
        
        if total_weight <= 0:
            return random.choice(responses)

        r = random.uniform(0, total_weight)
        upto = 0
        for response, weight in zip(responses, weights):
            upto += weight
            if upto > r:
                return response

        return responses[0]

    def _generate_fallback_response(self, context: Dict[str, any]) -> str:
        """Generate a fallback response when no database match is found"""
        # Check for common patterns in context
        if 'error' in context:
            return self.get_error_response()
        if 'success' in context:
            return self.get_success_response()
        if 'farewell' in context:
            return self.get_farewell_response()
        if 'needs_clarification' in context:
            return self.get_clarification_response()

        # Default response
        return "I understand. How can I help you further? (Main samajh gaya. Aur kya madad kar sakta hoon?)"

    def add_response_to_db(self, prompt: str, response: str, language: str = 'en') -> bool:
        """Add a new response to the database"""
        try:
            # Add response to database for future use
            db_manager.add_response(prompt, response, language)
            return True
        except Exception as e:
            logger.error(f"Error adding response to database: {e}")
            return False

# Initialize the response generator
response_generator = ResponseGenerator()

def get_response(response_type: str, context: Dict[str, any] = None) -> str:
    """
    Get a response of the specified type
    Args:
        response_type: Type of response needed ('error', 'success', 'farewell', etc.)
        context: Optional context dictionary for contextual responses
    Returns:
        str: Appropriate response
    """
    if context:
        return response_generator.get_contextual_response(context)

    response_map = {
        'error': response_generator.get_error_response,
        'success': response_generator.get_success_response,
        'farewell': response_generator.get_farewell_response,
        'clarification': response_generator.get_clarification_response
    }

    response_func = response_map.get(response_type)
    if response_func:
        return response_func()
    
    return response_generator.get_error_response('general') 