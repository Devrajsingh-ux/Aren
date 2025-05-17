# Chat-based assistant functionality
import pyttsx3
import threading
from queue import Queue
from typing import Optional
from loguru import logger
import re

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Get available voices and set a default
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        
        # Queue for speech requests
        self.speech_queue = Queue()
        self.is_speaking = False
        
        # Start the speech thread
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text to make it more suitable for speech
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Add pauses for punctuation
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
        
        return text.strip()
    
    def _speech_worker(self):
        """Background worker for processing speech requests"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:
                    break
                
                # Preprocess the text
                processed_text = self._preprocess_text(text)
                
                if not processed_text:
                    continue
                
                self.is_speaking = True
                self.engine.say(processed_text)
                self.engine.runAndWait()
                self.is_speaking = False
                
            except Exception as e:
                logger.error(f"Error in speech worker: {e}")
                self.is_speaking = False
    
    def speak_text(self, text: str) -> None:
        """
        Add text to the speech queue
        
        Args:
            text: Text to speak
        """
        try:
            if not text or not isinstance(text, str):
                logger.warning("Invalid text input for speech")
                return
                
            self.speech_queue.put(text)
        except Exception as e:
            logger.error(f"Error queuing speech: {e}")
    
    def stop_speaking(self) -> None:
        """Stop any ongoing speech"""
        try:
            self.engine.stop()
            self.is_speaking = False
            # Clear the queue
            while not self.speech_queue.empty():
                self.speech_queue.get()
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def is_currently_speaking(self) -> bool:
        """Check if text is currently being spoken"""
        return self.is_speaking
    
    def set_voice(self, voice_id: str) -> None:
        """
        Set the voice to use for speech
        
        Args:
            voice_id: ID of the voice to use
        """
        try:
            self.engine.setProperty('voice', voice_id)
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
    
    def set_rate(self, rate: int) -> None:
        """
        Set the speech rate
        
        Args:
            rate: Words per minute (default is 150)
        """
        try:
            if rate > 0:
                self.engine.setProperty('rate', rate)
        except Exception as e:
            logger.error(f"Error setting speech rate: {e}")
    
    def set_volume(self, volume: float) -> None:
        """
        Set the speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            if 0.0 <= volume <= 1.0:
                self.engine.setProperty('volume', volume)
        except Exception as e:
            logger.error(f"Error setting volume: {e}")

# Initialize text-to-speech engine
tts_engine = TextToSpeech()

def speak_text(text: str) -> None:
    """
    Speak the given text
    
    Args:
        text: Text to speak
    """
    tts_engine.speak_text(text)

def stop_speaking() -> None:
    """Stop any ongoing speech"""
    tts_engine.stop_speaking()

def is_speaking() -> bool:
    """Check if text is currently being spoken"""
    return tts_engine.is_currently_speaking()

# Test the text-to-speech functionality
if __name__ == "__main__":
    print("Testing text-to-speech...")
    speak_text("Hello! This is a test of the text to speech system.")
    # Wait for speech to complete
    while is_speaking():
        pass
    print("Test completed!")
