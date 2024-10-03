import speech_recognition as sr
import pywhatkit as kit
import webbrowser

# Importing from your brain module
from brain.speak import speak

# Speak function using brain.speak
def talk(text):
    print(f"Assistant: {text}")
    speak(text)

# Take command function with error handling
def take_command():
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        listener.adjust_for_ambient_noise(source, duration=1)  # Adjust to ambient noise
        voice = listener.listen(source)
    try:
        command = listener.recognize_google(voice)
        command = command.lower()
        if 'assistant' in command:
            command = command.replace('assistant', '').strip()
            print(f"Command received: {command}")
    except sr.UnknownValueError:
        talk("Sorry, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        talk("Sorry, I couldn't connect to the speech recognition service.")
        return ""
    return command

# Enhanced YouTube search and control without pyautogui
def youtube_search(command):
    if "play" in command:
        video_name = command.replace("play", "").strip()
        talk(f"Playing {video_name} on YouTube.")
        kit.playonyt(video_name)  # Use pywhatkit to play directly on YouTube
    elif "open my channel" in command:
        talk("Opening your channel on YouTube")
        webbrowser.open("https://youtube.com/@mr.devshakya?si=f2ksFr3PyUlh1iqs")
    else:
        talk("I couldn't find anything related to your YouTube request.")

# Direct YouTube player control using JavaScript injection
def control_youtube(command):
    js_command = ""
    
    if "pause" in command:
        js_command = "document.querySelector('video').pause()"
    elif "play" in command:
        js_command = "document.querySelector('video').play()"
    elif "mute" in command:
        js_command = "document.querySelector('video').muted = true"
    elif "unmute" in command:
        js_command = "document.querySelector('video').muted = false"
    elif "full screen" in command:
        js_command = "document.querySelector('video').requestFullscreen()"
    
    if js_command:
        talk(f"{command.capitalize()}ing video.")
        inject_js_into_browser(js_command)
    else:
        talk("Sorry, I couldn't understand your YouTube control request.")

# Function to inject JavaScript into the browser
def inject_js_into_browser(js_code):
    # Open the browser's developer tools with the following command to execute JavaScript directly
    # This requires a browser extension or manual setup to run JS on your browser from Python
    webbrowser.open(f"javascript:{js_code}", new=0)

# Main assistant function
def run_assistant():
    command = take_command()
    if 'play' in command:
        youtube_search(command)
    elif 'control' in command and 'youtube' in command:
        control_youtube(command)
    elif 'exit' in command or 'stop' in command:
        talk("Goodbye!")
        return False  # Stop the assistant
    else:
        talk("I didn't understand. Please say it again.")
    return True  # Continue running the assistant

if __name__ == "__main__":
    talk("Hello Dev Shakya, how can I assist you today?")
    while run_assistant():
        pass
