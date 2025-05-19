"""
Application automation capabilities for AREN
"""

import os
import subprocess
import platform
from utils.logging_utils import logger

def launch_application(app_name):
    """
    Launch an application based on the given name, with support for
    multiple languages and operating systems
    """
    app_name = app_name.lower()
    logger.info(f"Attempting to launch application: {app_name}")
    
    # English and Hindi/Hinglish mappings
    app_map = {
        'notepad': {
            'keywords': ['notepad', 'नोटपैड', 'note pad', 'open notepad', 'notepad kholo'],
            'windows': 'notepad.exe',
            'linux': 'gedit',
            'darwin': 'TextEdit'
        },
        'calculator': {
            'keywords': ['calculator', 'कैलकुलेटर', 'calc', 'calculator kholo', 'open calculator'],
            'windows': 'calc.exe',
            'linux': 'gnome-calculator',
            'darwin': 'Calculator'
        },
        'chrome': {
            'keywords': ['chrome', 'क्रोम', 'google chrome', 'chrome kholo', 'open chrome'],
            'windows': 'chrome.exe',
            'linux': 'google-chrome',
            'darwin': 'Google\\ Chrome'
        },
        'firefox': {
            'keywords': ['firefox', 'mozilla', 'फायरफॉक्स', 'firefox kholo', 'open firefox'],
            'windows': 'firefox.exe',
            'linux': 'firefox',
            'darwin': 'Firefox'
        }
    }
    
    current_os = platform.system().lower()
    
    for app, details in app_map.items():
        if any(keyword in app_name for keyword in details['keywords']):
            try:
                # Get the command for the current OS
                if current_os == 'windows':
                    os.startfile(details['windows'])
                elif current_os == 'darwin':  # macOS
                    subprocess.Popen(['open', '-a', details['darwin']])
                elif current_os == 'linux':
                    subprocess.Popen([details['linux']])
                else:
                    return f"Sorry, your operating system ({platform.system()}) is not supported."
                
                logger.info(f"Successfully launched {app}")
                return f"{app.title()} launched successfully!"
            except Exception as e:
                logger.error(f"Failed to launch {app}: {str(e)}")
                return f"Failed to launch {app}: {e}"
    
    logger.warning(f"Could not recognize application: {app_name}")
    return "Sorry, I couldn't recognize the application to launch." 