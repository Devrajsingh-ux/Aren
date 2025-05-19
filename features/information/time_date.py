"""
Time and date related functionality for AREN
"""

from datetime import datetime

def get_current_time():
    """Get the current time as a formatted string"""
    return datetime.now().strftime('%H:%M:%S')

def get_current_date():
    """Get the current date as a formatted string"""
    return datetime.now().strftime('%Y-%m-%d')

def get_time_of_day():
    """Return the current time of day category"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 22:
        return 'evening'
    else:
        return 'night' 