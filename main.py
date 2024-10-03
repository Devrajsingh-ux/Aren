from brain.speak import speak, listen
from brain.greetMe import get_greeting


if __name__ == "__main__":
    command = listen()
    if command and ("hey buddy" in command.lower() or "wake up buddy" in command.lower()): 
        active = True
        greeting = get_greeting()
        speak(greeting)  # Speak the greeting
       
        while True:
            command = listen()
            if not command:
                continue
            # Handle conversation
            from brain.conversation import general_responses,choose_personality,keep_conversation_flowing,start_conversation,handle_conversation,small_talk,user_day_responses,personalities
            response = handle_conversation(command)
            if response:
                speak(response)
                continue


            elif "rest" in command.lower():
                speak("Goodbye!")
                break
            elif "sleep" in command.lower():
                speak("I'm going to sleep")
                active = False
                while not active:
                    print("sleeping...")
                    command = listen()
                    if command and ("friday" in command.lower()):
                        active = True
                        speak("at your service sir")