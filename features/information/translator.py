"""
Translation capabilities for AREN
This module handles translation between languages.
"""

import re
import requests
import os
import json
import random
from utils.logging_utils import logger

# LibreTranslate API URL - using a public instance, but can be changed
API_URL = "https://translate.argosopentech.com/translate"

# Common language codes
LANGUAGE_CODES = {
    "english": "en",
    "hindi": "hi",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh",
    "russian": "ru",
    "arabic": "ar",
    "bengali": "bn",
    "urdu": "ur",
    "punjabi": "pa",
    "tamil": "ta",
    "telugu": "te",
    "marathi": "mr",
    "gujarati": "gu"
}

# Built-in translations for common phrases
BUILT_IN_TRANSLATIONS = {
    ("hello", "es"): "hola",
    ("hello", "hi"): "नमस्ते",
    ("hello", "fr"): "bonjour",
    ("goodbye", "es"): "adiós",
    ("goodbye", "hi"): "अलविदा",
    ("goodbye", "fr"): "au revoir",
    ("thank you", "es"): "gracias",
    ("thank you", "hi"): "धन्यवाद",
    ("thank you", "fr"): "merci"
}

def extract_translation_request(user_input):
    """
    Extract translation details from user input
    Returns: (text_to_translate, target_language, source_language)
    """
    # Normalize input
    input_lower = user_input.lower()
    
    # Comprehensive translation request patterns
    translation_patterns = [
        # Direct translation patterns
        r'translate\s*["\']?(.+?)["\']?\s*(?:to|in)\s*([a-zA-Z]+)',
        # "What is X in Y" patterns
        r'(?:what\s+is|how\s+do\s+you\s+say)\s*["\']?(.+?)["\']?\s*(?:in|to)\s*([a-zA-Z]+)',
        # Alternate phrasing
        r'(.+?)\s*(?:to|in)\s*([a-zA-Z]+)\s*language'
    ]
    
    # Try each pattern
    for pattern in translation_patterns:
        match = re.search(pattern, input_lower)
        if match:
            text = match.group(1).strip().strip('"\'')
            target_lang_name = match.group(2).strip()
            
            # Convert language name or code to standard code
            target_lang_code = get_language_code(target_lang_name)
            
            if target_lang_code:
                return text, target_lang_code, 'auto'
    
    # Fallback
    return None, None, None

def translate_text(text, target_lang, source_lang='auto'):
    """
    Translate text using multiple strategies
    """
    if not text or not target_lang:
        return "Invalid translation request"
    
    # Check built-in translations first
    built_in_key = (text.lower(), target_lang)
    if built_in_key in BUILT_IN_TRANSLATIONS:
        logger.info(f"Used built-in translation for '{text}' to {target_lang}")
        return BUILT_IN_TRANSLATIONS[built_in_key]
    
    try:
        # Try LibreTranslate API
        response = requests.post(API_URL, json={
            'q': text,
            'source': source_lang,
            'target': target_lang
        })
        
        if response.status_code == 200:
            translated_text = response.json().get('translatedText', '')
            logger.info(f"Translated '{text}' to {target_lang} using LibreTranslate")
            return translated_text
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
    
    # Fallback to a generic response
    logger.warning("Translation failed. Using fallback method.")
    return f"Translation to {target_lang} unavailable. Original text: {text}"

def get_fallback_translation(text, target_lang_code):
    """
    Provide a fallback mechanism when API translation fails
    
    Args:
        text (str): Text to translate
        target_lang_code (str): Target language code
        
    Returns:
        str: Best-effort translation or message
    """
    text_lower = text.lower().strip()
    
    # Split input and look for word-by-word translations in our dictionary
    words = text_lower.split()
    if len(words) <= 3:  # Only attempt for short phrases
        if any(word in BUILT_IN_TRANSLATIONS for word in words):
            # If any word matches our dictionary, use it
            translated_parts = []
            for word in words:
                if word in BUILT_IN_TRANSLATIONS and target_lang_code in BUILT_IN_TRANSLATIONS[word]:
                    translated_parts.append(BUILT_IN_TRANSLATIONS[word][target_lang_code])
                else:
                    translated_parts.append(f"[{word}]")  # Keep untranslated words in brackets
            
            translated_text = " ".join(translated_parts)
            logger.info(f"Used partial built-in translation for '{text}' to {target_lang_code}")
            return f"Translation to {get_language_name(target_lang_code)} (approximate):\n{translated_text}"
    
    # For numbers, letters, and simple terms, do a naive translation
    if text.isdigit():
        return f"Translation to {get_language_name(target_lang_code)}:\n{text}"
    
    # If all else fails, provide a helpful message about the failure
    lang_name = get_language_name(target_lang_code)
    sample_translations = []
    for key, translations in BUILT_IN_TRANSLATIONS.items():
        if target_lang_code in translations:
            sample_translations.append(f"'{key}' → '{translations[target_lang_code]}'")
            if len(sample_translations) >= 3:
                break
    
    if sample_translations:
        samples = ", ".join(sample_translations)
        message = (f"I'm having trouble translating that to {lang_name} right now.\n\n"
                  f"Here are some {lang_name} phrases I know: {samples}")
    else:
        message = f"I'm having trouble translating to {lang_name} right now. Please try again later."
    
    return message

def get_language_code(language):
    """
    Convert a language name to its code
    
    Args:
        language (str): Language name or code
        
    Returns:
        str: Language code or None if not found
    """
    if not language:
        return None
        
    language = language.lower()
    
    # If already a valid 2-letter code, return it
    if language in LANGUAGE_CODES.values():
        return language
        
    # Otherwise look up by name
    return LANGUAGE_CODES.get(language)

def get_language_name(code):
    """
    Convert a language code to its name
    
    Args:
        code (str): Language code
        
    Returns:
        str: Language name or the code if not found
    """
    for name, lang_code in LANGUAGE_CODES.items():
        if lang_code == code:
            return name.capitalize()
    return code 