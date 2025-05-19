from datetime import datetime
from features.search import web_search
from features.automation import launch_application
from features.personality import get_greeting, get_joke, get_identity

def process_input(user_input):
    user_input_lower = user_input.lower()
    # Time/Date
    if any(x in user_input_lower for x in ["time", "samay", "kitna baj gaya", "what's the time"]):
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
    elif any(x in user_input_lower for x in ["date", "aaj ki tareekh", "today's date", "what's the date"]):
        return f"Today's date is {datetime.now().strftime('%Y-%m-%d')}"
    # Web search
    search_triggers = ["search ", "look up ", "who is ", "what is ", "when is ", "where is ", "why is ", "how do", "how to", "tell me about ", "kya hai", "kaun hai", "batao"]
    if any(user_input_lower.startswith(trigger) or trigger in user_input_lower for trigger in search_triggers):
        return web_search(user_input)
    # Application launching
    app_triggers = ["open ", "launch ", "start ", "khol", "chalu karo", "shuru karo"]
    if any(trigger in user_input_lower for trigger in app_triggers):
        return launch_application(user_input)
    # Greetings
    greeting_triggers = ["hello", "hi", "namaste", "hey", "salaam", "pranam"]
    if any(trigger in user_input_lower for trigger in greeting_triggers):
        return get_greeting()
    # Jokes
    joke_triggers = ["joke", "mazaak", "funny", "kuch funny bolo", "kuch mazaak batao"]
    if any(trigger in user_input_lower for trigger in joke_triggers):
        return get_joke()
    # Identity
    identity_triggers = ["who are you", "tum kaun ho", "what is your name", "naam kya hai", "about yourself", "introduce yourself"]
    if any(trigger in user_input_lower for trigger in identity_triggers):
        return get_identity()
    return "I'm not sure how to help with that yet. (Main samajh nahi paaya, dobara poochhein!)" 