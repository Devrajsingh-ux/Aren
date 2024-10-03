import pyttsx3
import speech_recognition as sr

# Initialize TTS Engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Adjust rate of speech
voices = engine.getProperty('voices')

# Set default voice (change to voices[0] for a male voice)
engine.setProperty('voice', voices[1].id)  # voices[1] for female  & voices[0] for male

# Function to speak text
def speak(text):
    print(f"FRIDAY: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to listen and recognize speech
def listen(language='en-in'):
    recognizer = sr.Recognizer()

    # Adjust sensitivity and dynamic threshold
    recognizer.energy_threshold = 200
    recognizer.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        try:
            # Listen with a timeout for non-responsiveness
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)  # Increased phrase time limit
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for a response")
            return ""  # Return empty string if nothing heard
    
    # Try to recognize speech
    try:
        command = recognizer.recognize_google(audio, language='en-in')  # Set language to Hindi
        print(f"DEV: {command}")  # Log user's command
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry")
        return ""  # Return empty string if not understood
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""  # Return empty string on request error

