"""
Decision making system for AREN
This module contains the logic for AREN's decision making capabilities.
"""

import random
from datetime import datetime
import re
from typing import Dict, List, Tuple, Any
from utils.logging_utils import logger

class DecisionMaker:
    def __init__(self):
        self.decision_history = []
        self.confidence_threshold = 0.7
        self.last_decision_time = None
        
        # Patterns for intent recognition with confidence weights
        self.intent_patterns = {
            'time': {
                'patterns': [
                    (r'\b(?:what(?:\'s| is) the time|current time|time now)\b', 1.0),
                    (r'\b(?:samay kya hai|kitne baje|\btime\b)\b', 0.9),
                    (r'\b(?:tell me the time|check time)\b', 0.8)
                ],
                'keywords': ['time', 'samay', 'baje', 'clock']
            },
            'date': {
                'patterns': [
                    (r'\b(?:what(?:\'s| is) the date|current date|date today|today(?:\'s)? date)\b', 1.0),
                    (r'\b(?:aaj ki date|tareekh|\bdate\b)\b', 0.9),
                    (r'\b(?:tell me the date|check date)\b', 0.8)
                ],
                'keywords': ['date', 'tareekh', 'today', 'aaj']
            },
            'identity': {
                'patterns': [
                    (r'\b(?:who are you|what are you|what is your name)\b', 1.0),
                    (r'\b(?:tell me about yourself|introduce yourself)\b', 0.9),
                    (r'\b(?:kaun ho|naam kya|kya kar sakte ho)\b', 0.9),
                    (r'\b(?:what can you do|your capabilities)\b', 0.8)
                ],
                'keywords': ['you', 'your', 'name', 'naam', 'kaun', 'who']
            },
            'greeting': {
                'patterns': [
                    (r'\b(?:hello|hi|hey|namaste|namaskar)\b', 1.0),
                    (r'\b(?:good morning|good afternoon|good evening)\b', 0.9),
                    (r'\b(?:hola|pranaam)\b', 0.8)
            ],
                'keywords': ['hello', 'hi', 'hey', 'namaste', 'good']
            },
            'joke': {
                'patterns': [
                    (r'\b(?:tell (?:me )?a joke|make me laugh)\b', 1.0),
                    (r'\b(?:joke sunao|koi joke)\b', 0.9),
                    (r'\b(?:funny|mazaak|masti|entertain)\b', 0.8)
            ],
                'keywords': ['joke', 'funny', 'laugh', 'mazaak']
            },
            'launch_app': {
                'patterns': [
                    (r'\b(?:open|launch|start|run|execute) (?:the )?(.*?)(?:\s|$)', 1.0),
                    (r'\b(?:kholo|shuru karo|chalao) (.*?)(?:\s|$)', 0.9)
            ],
                'keywords': ['open', 'launch', 'start', 'run', 'kholo']
            },
            'search': {
                'patterns': [
                    (r'\b(?:search for|look up|find|tell me about)\b', 1.0),
                    (r'\b(?:what is|who is|how to|when did|where is|why does)\b', 0.9),
                    (r'\b(?:can you find|information about)\b', 0.8)
            ],
                'keywords': ['search', 'find', 'what', 'who', 'how', 'when', 'where', 'why']
            },
            'weather': {
                'patterns': [
                    (r'\b(?:weather|temperature|forecast)\b', 1.0),
                    (r'\b(?:mausam|garmi|sardi|barish)\b', 0.9),
                    (r'\b(?:rain|sunny|cloudy)\b', 0.8)
            ],
                'keywords': ['weather', 'temperature', 'mausam', 'forecast']
            },
            'calculation': {
                'patterns': [
                    (r'\b(?:calculate|compute|add|subtract|multiply|divide)\b', 1.0),
                    (r'\b(?:equal|equals|percentage|percent)\b', 0.9),
                    (r'(\d+[\+\-\*\/\^]\d+)', 1.0),  # Basic arithmetic patterns
                    (r'\b(?:sum|square root|cube)\b', 0.8)
            ],
                'keywords': ['calculate', 'compute', 'sum', 'add', 'multiply']
            },
            'translate': {
                'patterns': [
                    (r'\b(?:translate|translation|convert to)\b', 1.0),
                    (r'\b(?:in (?:english|hindi|spanish))\b', 0.9),
                    (r'\b(?:meaning|anuvad)\b', 0.8)
                ],
                'keywords': ['translate', 'translation', 'meaning', 'anuvad']
            }
        }
    
    def make_decision(self, capability_options: List[str], context: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Make a decision about which capability to use based on input and context
        Returns: (selected_capability, confidence_score, reasoning)
        """
        try:
            user_input = context.get('user_input', '').lower()
            input_tokens = set(user_input.split())
            
            # Track decision time
            self.last_decision_time = datetime.now()
            
            # Calculate confidence scores for each capability
            scores = []
            for capability in capability_options:
                if capability not in self.intent_patterns:
                    continue
                
                patterns = self.intent_patterns[capability]
                score = 0.0
                matches = []
                
                # Check regex patterns
                for pattern, weight in patterns['patterns']:
                    if re.search(pattern, user_input):
                        score = max(score, weight)
                        matches.append(f"Pattern match: {pattern}")
            
                # Check keywords
                keyword_matches = set(patterns['keywords']) & input_tokens
                if keyword_matches:
                    keyword_score = len(keyword_matches) / len(patterns['keywords']) * 0.8
                    score = max(score, keyword_score)
                    matches.append(f"Keyword matches: {', '.join(keyword_matches)}")
            
                # Context-based adjustments
                if context.get('historical'):
                    # Check recent actions
                    recent_actions = context['historical'].get('session', {}).get('recent_actions', [])
                    for action in recent_actions[-3:]:  # Look at last 3 actions
                        if action['type'] == capability:
                            score *= 0.9  # Slightly reduce score for recently used capabilities
                            matches.append("Recent usage adjustment")
                
                if score > 0:
                    scores.append((capability, score, matches))
            
            if not scores:
                # No matches found, default to 'unknown' with low confidence
                return 'unknown', 0.5, "No clear intent matches found"
            
            # Sort by confidence score
            scores.sort(key=lambda x: x[1], reverse=True)
            selected, confidence, matches = scores[0]
            
            # Record the decision
            decision = {
                'timestamp': datetime.now().isoformat(),
                'input': user_input,
                'selected': selected,
                'confidence': confidence,
                'matches': matches
            }
            self.decision_history.append(decision)
            
            # Trim history if too long
            if len(self.decision_history) > 100:
                self.decision_history = self.decision_history[-100:]
            
            reasoning = f"Selected based on: {'; '.join(matches)}"
            logger.info(f"Selected '{selected}' with confidence {confidence:.2f}")
            
            return selected, confidence, reasoning
            
        except Exception as e:
            logger.error(f"Error in decision making: {e}")
            return 'unknown', 0.5, f"Error in decision making: {str(e)}"
    
    def get_decision_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        return self.decision_history[-limit:]
    
    def get_confidence_explanation(self, capability: str, confidence: float) -> str:
        """Generate an explanation for the confidence score"""
        if confidence >= 0.9:
            return f"Very confident this is a {capability} request"
        elif confidence >= 0.7:
            return f"Fairly confident this is a {capability} request"
        elif confidence >= 0.5:
            return f"Moderately confident this might be a {capability} request"
        else:
            return "Not very confident about this request" 