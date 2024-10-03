import datetime
from brain.speak import speak


def get_greeting():
    current_hour = datetime.datetime.now().hour
    if 6 <= current_hour < 12:
        return "Good morning SIR"
    elif 12 <= current_hour < 18:
        return "Good afternoon SIR"
    elif 18 <= current_hour < 21:
        return "Good evening SIR"
    else:
        return "yes SIR"

if __name__ == "__main__":
        # Greeting
    now = datetime.datetime.now()
    greeting = get_greeting()
    speak(f"{greeting}, I'm FRIDAY, At your service sir")
   

    pass