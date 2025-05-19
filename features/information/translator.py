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
    "hello": {
        "hi": "नमस्ते",
        "es": "hola",
        "fr": "bonjour",
        "de": "hallo",
        "it": "ciao",
        "ja": "こんにちは",
        "zh": "你好",
        "ru": "привет"
    },
    "goodbye": {
        "hi": "अलविदा",
        "es": "adiós",
        "fr": "au revoir",
        "de": "auf wiedersehen",
        "it": "arrivederci",
        "ja": "さようなら",
        "zh": "再见",
        "ru": "до свидания"
    },
    "thank you": {
        "hi": "धन्यवाद",
        "es": "gracias",
        "fr": "merci",
        "de": "danke",
        "it": "grazie",
        "ja": "ありがとう",
        "zh": "谢谢",
        "ru": "спасибо"
    },
    "yes": {
        "hi": "हां",
        "es": "sí",
        "fr": "oui",
        "de": "ja",
        "it": "sì",
        "ja": "はい",
        "zh": "是的",
        "ru": "да"
    },
    "no": {
        "hi": "नहीं",
        "es": "no",
        "fr": "non",
        "de": "nein",
        "it": "no",
        "ja": "いいえ",
        "zh": "不",
        "ru": "нет"
    },
    "please": {
        "hi": "कृपया",
        "es": "por favor",
        "fr": "s'il vous plaît",
        "de": "bitte",
        "it": "per favore",
        "ja": "お願いします",
        "zh": "请",
        "ru": "пожалуйста"
    },
    "sorry": {
        "hi": "माफ़ कीजिए",
        "es": "lo siento",
        "fr": "désolé",
        "de": "entschuldigung",
        "it": "scusa",
        "ja": "ごめんなさい",
        "zh": "对不起",
        "ru": "извините"
    },
    "good morning": {
        "hi": "शुभ प्रभात",
        "es": "buenos días",
        "fr": "bonjour",
        "de": "guten morgen",
        "it": "buongiorno",
        "ja": "おはようございます",
        "zh": "早上好",
        "ru": "доброе утро"
    },
    "good night": {
        "hi": "शुभ रात्रि",
        "es": "buenas noches",
        "fr": "bonne nuit",
        "de": "gute nacht",
        "it": "buona notte",
        "ja": "おやすみなさい",
        "zh": "晚安",
        "ru": "спокойной ночи"
    },
    "how are you": {
        "hi": "आप कैसे हैं",
        "es": "cómo estás",
        "fr": "comment allez-vous",
        "de": "wie geht es dir",
        "it": "come stai",
        "ja": "お元気ですか",
        "zh": "你好吗",
        "ru": "как дела"
    }
}

def translate_text(text, target_lang, source_lang=None):
    """
    Translate text from source language to target language
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code or name
        source_lang (str, optional): Source language code or name. Auto-detect if None.
        
    Returns:
        str: Translated text or error message
    """
    try:
        # Convert language names to codes if needed
        target_lang_code = get_language_code(target_lang)
        source_lang_code = get_language_code(source_lang) if source_lang else "auto"
        
        # Check if target language is supported
        if not target_lang_code:
            return f"Sorry, I don't support translation to {target_lang}. (Main {target_lang} mein anuvad nahi kar sakta.)"
        
        # Check for built-in translations first
        text_lower = text.lower().strip()
        if text_lower in BUILT_IN_TRANSLATIONS and target_lang_code in BUILT_IN_TRANSLATIONS[text_lower]:
            translated_text = BUILT_IN_TRANSLATIONS[text_lower][target_lang_code]
            logger.info(f"Used built-in translation for '{text}' to {target_lang_code}")
            return f"Translation to {get_language_name(target_lang_code)}:\n{translated_text}"
        
        # If not a built-in phrase, try API
        try:
            # Prepare the request payload
            payload = {
                "q": text,
                "source": source_lang_code if source_lang_code != "auto" else "en",
                "target": target_lang_code,
                "format": "text"
            }
            
            # Make API request
            response = requests.post(API_URL, json=payload, timeout=5)
            
            if response.status_code == 200:
                # Extract translation from response
                result = response.json()
                translated_text = result.get("translatedText", "")
                
                if translated_text:
                    logger.info(f"Translated text from {source_lang_code} to {target_lang_code}")
                    return f"Translation to {get_language_name(target_lang_code)}:\n{translated_text}"
            
            # If API fails, try fallback method
            return get_fallback_translation(text, target_lang_code)
                
        except Exception as e:
            logger.error(f"Translation API error: {str(e)}")
            return get_fallback_translation(text, target_lang_code)
            
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return get_fallback_translation(text, target_lang_code)

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

def extract_translation_request(user_input):
    """
    Extract text and target language from a translation request
    
    Args:
        user_input (str): User's input text
        
    Returns:
        tuple: (text_to_translate, target_language, source_language) or (None, None, None) if not a translation request
    """
    # Common translation request patterns
    patterns = [
        # "translate X to Y"
        r'translate\s+["\']?(.+?)["\']?\s+(?:to|into|in|for)\s+([a-zA-Z]+)',
        # "translate X in Y"
        r'translate\s+["\']?(.+?)["\']?\s+(?:to|into|in|for)\s+([a-zA-Z]+)',
        # "X in Y language"
        r'["\']?(.+?)["\']?\s+(?:to|into|in)\s+([a-zA-Z]+)(?:\s+language)?',
        # "what is X in Y"
        r'what\s+(?:is|does)\s+["\']?(.+?)["\']?\s+mean\s+(?:in|on)\s+([a-zA-Z]+)',
        # "how do you say X in Y"
        r'how\s+(?:do|would|can|to)\s+(?:you|I|we)?\s+say\s+["\']?(.+?)["\']?\s+in\s+([a-zA-Z]+)',
        # Hindi patterns
        r'(.+?)\s+(?:ka|ko)\s+([a-zA-Z]+)\s+(?:mein|me|anuvad)'
    ]
    
    user_input_lower = user_input.lower()
    
    # Check for translation keywords first
    if not any(keyword in user_input_lower for keyword in ["translate", "translation", "meaning", "anuvad", "bhasha"]):
        return None, None, None
    
    # Try each pattern
    for pattern in patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            text_to_translate = match.group(1).strip()
            target_language = match.group(2).strip()
            
            # Remove quotes if present
            text_to_translate = text_to_translate.strip('"\'')
            
            return text_to_translate, target_language, None
    
    # Handle "translate X" (without specifying target language)
    translate_pattern = r'translate\s+["\']?(.+?)["\']?$'
    match = re.search(translate_pattern, user_input_lower)
    if match:
        text_to_translate = match.group(1).strip().strip('"\'')
        # Default to Hindi if no target language specified
        return text_to_translate, "hindi", None
    
    return None, None, None 