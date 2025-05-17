import logging
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
import re
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class QuestionClassifier:
    def __init__(self):
        self.question_types = {
            'search': [
                'what is', 'how to', 'where is', 'when is', 'who is',
                'search for', 'find', 'look up', 'tell me about'
            ],
            'details': [
                'explain', 'describe', 'details about', 'more information',
                'elaborate', 'break down'
            ],
            'dna': [
                'analyze dna', 'dna sequence', 'genetic', 'genome',
                'chromosome', 'gene', 'mutation'
            ],
            'calculation': [
                'calculate', 'compute', 'solve', 'result of',
                'answer to', 'sum of', 'product of'
            ],
            'comparison': [
                'compare', 'difference between', 'versus', 'vs',
                'better than', 'worse than'
            ]
        }
        self.vectorizer = TfidfVectorizer()
        self._train_vectorizer()

    def _train_vectorizer(self):
        """Train the TF-IDF vectorizer on question patterns."""
        all_patterns = []
        for patterns in self.question_types.values():
            all_patterns.extend(patterns)
        self.vectorizer.fit(all_patterns)

    def classify_question(self, text: str) -> str:
        """Classify the type of question being asked."""
        text_vector = self.vectorizer.transform([text])
        patterns_vector = self.vectorizer.transform(self.vectorizer.get_feature_names_out())
        
        similarities = cosine_similarity(text_vector, patterns_vector)[0]
        max_sim_idx = np.argmax(similarities)
        
        if similarities[max_sim_idx] > 0.3:  # Threshold for classification
            pattern = self.vectorizer.get_feature_names_out()[max_sim_idx]
            for qtype, patterns in self.question_types.items():
                if pattern in patterns:
                    return qtype
        return 'general'

class ReasoningEngine:
    def __init__(self):
        self.knowledge_base = {}
        self.rules = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load knowledge base from file."""
        try:
            kb_file = Path("data/knowledge_base.json")
            if kb_file.exists():
                with open(kb_file, 'r') as f:
                    self.knowledge_base = json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")

    def _save_knowledge_base(self):
        """Save knowledge base to file."""
        try:
            kb_file = Path("data/knowledge_base.json")
            kb_file.parent.mkdir(exist_ok=True)
            with open(kb_file, 'w') as f:
                json.dump(self.knowledge_base, f)
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")

    def add_knowledge(self, key: str, value: any):
        """Add new knowledge to the base."""
        self.knowledge_base[key] = value
        self._save_knowledge_base()

    def get_knowledge(self, key: str) -> Optional[any]:
        """Retrieve knowledge from the base."""
        return self.knowledge_base.get(key)

    def apply_rules(self, context: Dict) -> str:
        """Apply reasoning rules to the given context."""
        # Implement rule-based reasoning here
        pass

class MemorySystem:
    def __init__(self):
        self.short_term_memory = []
        self.long_term_memory = {}
        self.max_short_term = 100
        self._load_memory()

    def _load_memory(self):
        """Load long-term memory from file."""
        try:
            memory_file = Path("data/memory.json")
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    self.long_term_memory = json.load(f)
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")

    def _save_memory(self):
        """Save long-term memory to file."""
        try:
            memory_file = Path("data/memory.json")
            memory_file.parent.mkdir(exist_ok=True)
            with open(memory_file, 'w') as f:
                json.dump(self.long_term_memory, f)
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")

    def add_to_short_term(self, item: any):
        """Add item to short-term memory."""
        self.short_term_memory.append({
            'item': item,
            'timestamp': datetime.now().isoformat()
        })
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory.pop(0)

    def add_to_long_term(self, key: str, value: any):
        """Add item to long-term memory."""
        self.long_term_memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self._save_memory()

    def get_from_long_term(self, key: str) -> Optional[any]:
        """Retrieve item from long-term memory."""
        return self.long_term_memory.get(key)

    def consolidate_memory(self):
        """Move important short-term memories to long-term memory."""
        # Implement memory consolidation logic here
        pass

class ARENBrain:
    def __init__(self):
        self.question_classifier = QuestionClassifier()
        self.reasoning_engine = ReasoningEngine()
        self.memory_system = MemorySystem()
        self.context = {}

    def process_input(self, text: str) -> Tuple[str, Dict]:
        """Process input text and return response with context."""
        # Classify the question
        question_type = self.question_classifier.classify_question(text)
        
        # Add to short-term memory
        self.memory_system.add_to_short_term({
            'input': text,
            'type': question_type
        })
        
        # Get relevant knowledge
        knowledge = self.reasoning_engine.get_knowledge(question_type)
        
        # Apply reasoning
        response = self.reasoning_engine.apply_rules({
            'input': text,
            'type': question_type,
            'knowledge': knowledge,
            'context': self.context
        })
        
        # Update context
        self.context.update({
            'last_input': text,
            'last_type': question_type,
            'timestamp': datetime.now().isoformat()
        })
        
        return response, self.context

    def learn(self, input_text: str, response: str, success: bool):
        """Learn from interaction."""
        if success:
            self.reasoning_engine.add_knowledge(input_text, response)
            self.memory_system.add_to_long_term(
                f"successful_interaction_{datetime.now().isoformat()}",
                {'input': input_text, 'response': response}
            ) 