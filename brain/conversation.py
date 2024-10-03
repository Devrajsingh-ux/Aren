import datetime
import pyjokes
import speech_recognition as sr
from brain.speak import speak, listen



def calculate_age(birth_date):
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def get_random_joke():
    return pyjokes.get_joke()



def handle_conversation(command):
    responses = {
        "hello": "Hello sir",
        "hi": "Hello sir",
        "how are you": "I'm good, what about you sir?",
        "how r u": "I'm good, what about you sir?",
        "fine": "I'm glad to hear that you're fine sir.",
        "your name": "I'm Friday",
        "means of it": "FRIDAY means, FEMALE REPLACEMENT INTELLIGENT DIGITAL ASSISTANT YOUTH",
        "my name": "Your name is Dev Shakya",
        "my gender": "You are male",
        "my address": "Your address is Gwalior, Madhya Pradesh, India",
        "my phone number": "Your phone number is 918643079132",
        "my email": "Your email is devshakya666@gmail.com",
        "my hobbies": "Your hobbies are coding, playing PC games, listening to music",
        "my education": "Your education is B.Tech in Computer Science from Amity University, Gwalior",
        "who create you": "I am created by Dev Shakya",
        "my profession": "Your profession is a software engineer",
        "what can you do": "I can help you to do many things like search on Google, tell you about your friends, tell you about your family, tell you about your hobbies, tell you about your education, tell you about your profession",
        "where do you live": "I live in the digital world",
        "siblings": "I'm a Digital assistant, I don't have siblings",
        "favourite colour": "My favorite color is blue.",
        "date": "Today's date is " + datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": "The time is " + datetime.datetime.now().strftime("%H:%M"),
        "my details": "you are Dev shakya, you lived in Gwalior, Madhya Pradesh"
    }

    for key in responses:
        if key in command.lower():
            return responses[key]

    if "how old are you" in command.lower() or "your age" in command.lower():
        dob_input = "2024-06-23"  # Example date of birth
        try:
            birth_date = datetime.datetime.strptime(dob_input, "%Y-%m-%d")
            age = calculate_age(birth_date)
            speak(f"I am {age} years old sir.")
        except ValueError:
            speak("Invalid date format. Please enter the date in YYYY-MM-DD format.")
    elif "my age" in command.lower():
        dob_input = "2006-06-19"  # Example date of birth
        try:
            birth_date = datetime.datetime.strptime(dob_input, "%Y-%m-%d")
            age = calculate_age(birth_date)
            speak(f"You are {age} years old sir.")
        except ValueError:
            speak("Invalid date format. Please enter the date in YYYY-MM-DD format.")
    elif "joke" in command.lower() or "one more" in command.lower():
        joke = get_random_joke()
        speak(joke)

    return None

def main():
    while True:
        command = listen()
        if command:
            response = handle_conversation(command)
            if response:
                speak(response)

if __name__ == "__main__":
    main()
