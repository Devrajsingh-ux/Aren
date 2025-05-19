"""
Weather information capabilities for AREN
This module handles weather-related queries.
"""

import requests
import json
import os
import random
from datetime import datetime
from utils.logging_utils import logger

# OpenWeatherMap API base URL
API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(location=None):
    """
    Get current weather information for a specified location or default location
    
    Args:
        location (str, optional): The location to get weather for. If None, uses default location.
        
    Returns:
        str: Weather information in a readable format or error message
    """
    try:
        # Get API key from environment variable or use a default path
        # In a real implementation, you would store this securely
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        
        if not api_key:
            # Return mock data when API key is missing
            return get_mock_weather(location or "New Delhi")
        
        # Default to a major city if no location provided
        if not location:
            location = "New Delhi"  # Default location
        
        # Make request to OpenWeatherMap API
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'  # Use metric units (Celsius)
        }
        
        response = requests.get(API_BASE_URL, params=params)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            # Extract relevant data
            main_weather = weather_data['weather'][0]['main']
            description = weather_data['weather'][0]['description']
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            
            # Format response in both English and Hindi
            weather_message = (
                f"Weather in {location}: {main_weather} ({description})\n"
                f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"Humidity: {humidity}%\n\n"
                f"{location} mein mausam: {description}\n"
                f"Tapman: {temp}°C (mehsoos {feels_like}°C jaisa)\n"
                f"Namee: {humidity}%"
            )
            
            logger.info(f"Weather information retrieved for {location}")
            return weather_message
            
        elif response.status_code == 404:
            return f"Sorry, I couldn't find weather information for {location}. (Mujhe {location} ka mausam nahi mil raha hai.)"
        else:
            logger.error(f"Weather API error: {response.status_code}")
            return get_mock_weather(location)
            
    except Exception as e:
        logger.error(f"Error getting weather: {str(e)}")
        return get_mock_weather(location or "New Delhi")

def get_mock_weather(location):
    """
    Generate mock weather data when API is not available
    
    Args:
        location (str): Location to generate weather for
        
    Returns:
        str: Formatted mock weather information
    """
    # Mock weather conditions
    weather_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Clear Sky", "Light Rain", "Drizzle"]
    descriptions = ["clear sky", "few clouds", "scattered clouds", "light rainfall", "pleasant weather"]
    
    # Random weather generation
    condition = random.choice(weather_conditions)
    description = random.choice(descriptions)
    temp = round(random.uniform(20, 35), 1)
    feels_like = round(temp + random.uniform(-2, 3), 1)
    humidity = random.randint(40, 80)
    
    weather_message = (
        f"[SIMULATED] Weather in {location}: {condition} ({description})\n"
        f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
        f"Humidity: {humidity}%\n\n"
        f"{location} mein mausam: {description}\n"
        f"Tapman: {temp}°C (mehsoos {feels_like}°C jaisa)\n"
        f"Namee: {humidity}%"
    )
    
    logger.info(f"Generated mock weather for {location}")
    return weather_message

def extract_location(user_input):
    """
    Extract location from user input for weather queries
    
    Args:
        user_input (str): User input text
        
    Returns:
        str or None: Extracted location or None if not found
    """
    # Simple rule-based extraction - could be enhanced with NLP
    location_prefixes = [
        "weather in ", "weather for ", "temperature in ", "temperature for ",
        "weather at ", "mausam ", "weather of ", "weather forecast for ",
        "weather forecast in "
    ]
    
    user_input_lower = user_input.lower()
    
    for prefix in location_prefixes:
        if prefix in user_input_lower:
            # Extract everything after the prefix
            start_idx = user_input_lower.find(prefix) + len(prefix)
            location = user_input[start_idx:].strip()
            
            # Remove common end fragments
            end_fragments = [" like", " right now", " today", " tomorrow", "?", "."]
            for fragment in end_fragments:
                if fragment in location:
                    location = location.split(fragment)[0].strip()
            
            # If we have a valid location (at least 2 chars), return it
            if location and len(location) >= 2:
                return location
    
    # Check for standalone city after weather keyword
    weather_keywords = ["weather", "temperature", "forecast", "mausam", "temp"]
    for keyword in weather_keywords:
        if keyword in user_input_lower:
            words = user_input.split()
            keyword_index = None
            for i, word in enumerate(words):
                if keyword.lower() in word.lower():
                    keyword_index = i
                    break
            
            if keyword_index is not None and keyword_index < len(words) - 1:
                # Assume next word might be the location
                potential_location = words[keyword_index + 1]
                if len(potential_location) >= 2 and potential_location.lower() not in ["in", "for", "at", "of"]:
                    return potential_location
                elif keyword_index < len(words) - 2 and words[keyword_index + 1].lower() in ["in", "for", "at", "of"]:
                    # Handle "weather in Delhi" pattern
                    return words[keyword_index + 2]
    
    return None 