"""
Personality and interaction capabilities for AREN
"""

import random
from utils.logging_utils import logger
from features.information.time_date import get_time_of_day

def get_greeting():
    """Return a random greeting appropriate for the time of day"""
    time_of_day = get_time_of_day()
    
    greetings = {
        'morning': [
            "Good morning! How can I help you today?",
            "Suprabhat! Aaj main aapki kya madad kar sakta hoon?",
            "Good morning! Aaj ka din shubh ho."
        ],
        'afternoon': [
            "Good afternoon! How can I help you today?",
            "Namaskar! Kya haal hai?",
            "Hi there! Dopahar me kya karna chahte hain aap?"
        ],
        'evening': [
            "Good evening! How can I help you today?",
            "Shubh sandhya! Main A.R.E.N. hoon, aapki madad ke liye.",
            "Evening greetings! Kya poocha ja sakta hai?"
        ],
        'night': [
            "Hello! Working late tonight?",
            "Namaste! Raat me jaag rahe hain?",
            "Hi there! Kya main aapki kuch madad kar sakta hoon?"
        ]
    }
    
    # Get the appropriate list of greetings for the current time of day
    time_greetings = greetings.get(time_of_day, [
        "Hello! How can I help you today?",
        "Hi there! Kya haal hai?",
        "Namaste! Main A.R.E.N. hoon, aapki madad ke liye."
    ])
    
    selected_greeting = random.choice(time_greetings)
    logger.info(f"Selected greeting: {selected_greeting}")
    return selected_greeting

def get_joke():
    """Return a random joke"""
    jokes = [
        "Why did the computer go to the doctor? Because it had a virus!",
        "Main AI hoon, mujhe neend nahi aati!",
        "Why don't robots get scared? Kyunki unke paas dil nahi hota!",
        "What's a computer's favorite snack? Microchips!",
        "Why was the computer cold? It left its Windows open!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Computers make very fast, very accurate mistakes."
    ]
    selected_joke = random.choice(jokes)
    logger.info(f"Selected joke: {selected_joke}")
    return selected_joke

def get_identity():
    """Return AREN's identity information"""
    identity_responses = [
        "I am A.R.E.N., which stands for Assistant for Regular and Extraordinary Needs. "
        "I'm a Python-based AI assistant designed to help you with various tasks.",
        
        "My name is A.R.E.N. (Assistant for Regular and Extraordinary Needs). "
        "Main aapki madad ke liye hoon! I can help with searching information, "
        "telling time and date, launching applications, and more.",
        
        "I'm A.R.E.N., your AI assistant built in Python. "
        "I can handle tasks in both English and Hindi. "
        "Ask me about the time, date, to search for information, or to open applications!"
    ]
    
    selected_response = random.choice(identity_responses)
    logger.info("Identity information requested")
    return selected_response 