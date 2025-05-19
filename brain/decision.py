"""
Decision making system for AREN
This module contains the logic for AREN's decision making capabilities.
"""

import random
from datetime import datetime
import re
from utils.logging_utils import logger

class DecisionMaker:
    def __init__(self):
        self.decision_history = []
        self.confidence_threshold = 0.7
        self.last_decision_time = None
        # Patterns for intent recognition
        self.intent_patterns = {
            'time': [
                r'\b(?:what(?:\'s| is) the time|current time|time now|samay kya hai|kitne baje|\btime\b)\b',
            ],
            'date': [
                r'\b(?:what(?:\'s| is) the date|current date|date today|today(?:\'s)? date|aaj ki date|tareekh|\bdate\b)\b',
            ],
            'identity': [
                r'\b(?:who are you|what are you|what is your name|tell me about yourself|introduce yourself|kaun ho|naam kya|kya kar sakte ho)\b',
            ],
            'greeting': [
                r'\b(?:hello|hi|hey|namaste|namaskar|good morning|good afternoon|good evening|hola|pranaam)\b',
            ],
            'joke': [
                r'\b(?:tell (?:me )?a joke|make me laugh|joke sunao|koi joke|funny|mazaak|masti|entertain)\b',
            ],
            'launch_app': [
                r'\b(?:open|launch|start|run|execute|kholo|shuru karo|chalao) (?:the )?(.*?)(?:\s|$)',
            ],
            'search': [
                r'\b(?:search for|look up|find|tell me about|what is|who is|how to|when did|where is|why does|can you find|information about)\b',
            ],
            'weather': [
                r'\b(?:weather|temperature|forecast|mausam|garmi|sardi|barish|rain|sunny|cloudy)\b',
            ],
            'calculation': [
                r'\b(?:calculate|compute|add|subtract|multiply|divide|equal|equals|percentage|percent|sum|square root|cube)\b',
                r'(\d+[\+\-\*\/\^]\d+)',  # Basic arithmetic patterns
            ],
            'reminder': [
                r'\b(?:remind me|reminder|alert|notification|yaad dilao|yaad|notify)\b',
            ],
            'translate': [
                r'\b(?:translate|translation|meaning of|matlab|anuvad|bhasha)\b',
            ]
        }
    
    def make_decision(self, options, context=None, weights=None):
        """
        Make a decision among the given options.
        
        Args:
            options (list): List of possible decisions/actions
            context (dict, optional): Contextual information to aid the decision
            weights (list, optional): Weights for each option if not equally probable
            
        Returns:
            tuple: (selected_option, confidence_score, reasoning)
        """
        self.last_decision_time = datetime.now()
        logger.info(f"Making decision among options: {options}")
        
        # If no weights provided, assume equal probability
        if weights is None:
            weights = [1.0 / len(options)] * len(options)
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Calculate confidence and reasoning based on context
        confidence_scores, reasonings = self._calculate_confidence(options, context)
        
        # Combine weights with confidence
        final_scores = [w * c for w, c in zip(normalized_weights, confidence_scores)]
        
        # Get the option with highest score
        best_index = final_scores.index(max(final_scores))
        selected_option = options[best_index]
        confidence = confidence_scores[best_index]
        reasoning = reasonings[best_index]
        
        # Record this decision
        decision_record = {
            'timestamp': self.last_decision_time,
            'options': options,
            'selected': selected_option,
            'confidence': confidence,
            'reasoning': reasoning,
            'context': context
        }
        self.decision_history.append(decision_record)
        
        logger.info(f"Selected '{selected_option}' with confidence {confidence:.2f}")
        return (selected_option, confidence, reasoning)
    
    def _calculate_confidence(self, options, context=None):
        """
        Calculate confidence scores for each option based on context.
        Uses pattern matching and contextual clues for more accurate decisions.
        
        Returns:
            tuple: (list of confidence scores, list of reasoning strings)
        """
        # Without context, use random confidence values
        if not context or 'user_input' not in context:
            scores = [0.5 + random.random() * 0.5 for _ in options]
            reasonings = [self._generate_reasoning(score) for score in scores]
            return scores, reasonings
        
        user_input = context.get('user_input', '').lower()
        scores = []
        reasonings = []
        
        for option in options:
            base_score = 0.5
            reason_parts = []
            
            # Check for intent patterns
            if option in self.intent_patterns:
                for pattern in self.intent_patterns[option]:
                    if re.search(pattern, user_input, re.IGNORECASE):
                        pattern_bonus = 0.3
                        base_score += pattern_bonus
                        reason_parts.append(f"Matched pattern for {option}")
            
            # Check for keyword matches
            if 'keywords' in context:
                keyword_matches = [kw for kw in context['keywords'] 
                                  if kw.lower() in option.lower() or 
                                  any(kw.lower() in p.lower() for p in self.intent_patterns.get(option, []))]
                if keyword_matches:
                    keyword_bonus = min(0.1 * len(keyword_matches), 0.3)
                    base_score += keyword_bonus
                    reason_parts.append(f"Matched {len(keyword_matches)} keywords")
            
            # Consider conversation history for context
            if 'historical' in context and 'current_conversation' in context['historical']:
                recent_convo = context['historical']['current_conversation'][-3:] if context['historical']['current_conversation'] else []
                history_bonus = 0
                
                # Check if there are related topics in recent conversation
                for exchange in recent_convo:
                    if 'user_input' in exchange:
                        # If the same capability was used successfully recently, small boost
                        if any(p in exchange['user_input'].lower() for p in self.intent_patterns.get(option, [])):
                            history_bonus += 0.05
                
                if history_bonus > 0:
                    base_score += history_bonus
                    reason_parts.append("Consistent with conversation history")
            
            # Consider user preferences if available
            if ('historical' in context and 'user_preferences' in context['historical']
                    and option in context['historical']['user_preferences']):
                pref_bonus = 0.15
                base_score += pref_bonus
                reason_parts.append("Matched user preference")
            
            # Special case handling
            if option == 'unknown' and len(options) > 1:
                # Unknown should be a fallback option
                base_score = min(base_score, 0.6)
                reason_parts.append("Fallback option")
            
            # Normalize to 0-1 range
            final_score = min(max(base_score, 0.1), 1.0)
            scores.append(final_score)
            
            # Generate reasoning
            if reason_parts:
                reasoning = f"Confidence {final_score:.2f}: {'; '.join(reason_parts)}"
            else:
                reasoning = self._generate_reasoning(final_score)
            
            reasonings.append(reasoning)
            
        return scores, reasonings
    
    def _generate_reasoning(self, confidence):
        """Generate explanation for why a decision was made based on confidence score"""
        if confidence > 0.9:
            return f"High confidence ({confidence:.2f}): Strong pattern match and contextual relevance"
        elif confidence > 0.7:
            return f"Good confidence ({confidence:.2f}): Clear intent recognition"
        elif confidence > 0.5:
            return f"Moderate confidence ({confidence:.2f}): Partial pattern match"
        else:
            return f"Low confidence ({confidence:.2f}): Insufficient information"
    
    def get_decision_history(self):
        """Return the history of decisions made"""
        return self.decision_history
    
    def get_last_decision(self):
        """Return the last decision made"""
        if self.decision_history:
            return self.decision_history[-1]
        return None 