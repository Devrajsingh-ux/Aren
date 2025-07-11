import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import json
import os
import threading
import requests
from brain.engine import ArenEngine
from utils.logging_utils import logger

class ArenChatGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Aren Chat Interface")
        self.window.geometry("1000x700")
        
        # Initialize Aren's engine
        self.aren_engine = ArenEngine()
        
        # Flag for running status
        self.is_running = True
        
        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main container
        self.container = ctk.CTkFrame(self.window)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header frame
        self.create_header()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.container)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat display area
        self.create_chat_area()
        
        # Input area
        self.create_input_area()
        
        # Status bar
        self.create_status_bar()
        
        # Initialize chat history
        self.load_chat_history()
        
        # Display welcome message
        welcome_msg = "Welcome to A.R.E.N. (Assistant for Regular and Extraordinary Needs)\nType your message and press Enter to start chatting!"
        self.add_message("Aren", welcome_msg, datetime.now().strftime("%H:%M"))
        
        # Start time update thread
        self.update_thread = threading.Thread(target=self.update_time_and_status, daemon=True)
        self.update_thread.start()
        
        # Get location
        self.update_location()
        
        # Bind window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind Ctrl+C handler
        self.window.bind('<Control-c>', self.on_interrupt)
    
    def on_closing(self):
        """Handle window closing"""
        try:
            logger.info("Shutting down Aren GUI...")
            self.is_running = False
            self.window.quit()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
        finally:
            self.window.destroy()
    
    def on_interrupt(self, event=None):
        """Handle Ctrl+C interrupt"""
        self.on_closing()
    
    def create_header(self):
        """Create header with time, date, and status"""
        self.header_frame = ctk.CTkFrame(self.container)
        self.header_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Time and Date
        self.time_frame = ctk.CTkFrame(self.header_frame)
        self.time_frame.pack(side=tk.LEFT, padx=10)
        
        self.time_label = ctk.CTkLabel(self.time_frame, text="", font=("Arial", 14))
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        self.date_label = ctk.CTkLabel(self.time_frame, text="", font=("Arial", 14))
        self.date_label.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.header_frame)
        self.status_frame.pack(side=tk.RIGHT, padx=10)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="●", font=("Arial", 14), text_color="green")
        self.status_label.pack(side=tk.LEFT, padx=2)
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="Online", font=("Arial", 14))
        self.status_text.pack(side=tk.LEFT, padx=2)
    
    def create_chat_area(self):
        """Create the main chat display area"""
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = ctk.CTkTextbox(self.chat_frame, wrap=tk.WORD, font=("Arial", 12))
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.configure(state='disabled')
    
    def create_input_area(self):
        """Create the message input area"""
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_input = ctk.CTkTextbox(self.input_frame, height=60, wrap=tk.WORD, font=("Arial", 12))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 2), pady=5)
        
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            width=100,
            font=("Arial", 12)
        )
        self.send_button.pack(side=tk.RIGHT, padx=(2, 5), pady=5)
        
        # Bind Enter key to send message
        self.message_input.bind("<Return>", self.handle_return)
        self.message_input.bind("<Shift-Return>", self.handle_shift_return)
    
    def create_status_bar(self):
        """Create status bar with location info"""
        self.status_bar = ctk.CTkFrame(self.container)
        self.status_bar.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.location_label = ctk.CTkLabel(self.status_bar, text="Location: Detecting...", font=("Arial", 12))
        self.location_label.pack(side=tk.LEFT, padx=5)
    
    def update_time_and_status(self):
        """Update time, date and status periodically"""
        while self.is_running:
            try:
                current_time = datetime.now()
                self.time_label.configure(text=current_time.strftime("%I:%M:%S %p"))
                self.date_label.configure(text=current_time.strftime("%d %b %Y"))
                
                # Check Aren's status (simplified)
                try:
                    self.aren_engine.process_input("test")
                    self.status_label.configure(text_color="green")
                    self.status_text.configure(text="Online")
                except Exception:
                    self.status_label.configure(text_color="red")
                    self.status_text.configure(text="Offline")
                
                self.window.after(1000)  # Wait for 1 second
            except Exception as e:
                if self.is_running:  # Only log if not shutting down
                    logger.error(f"Error updating time/status: {str(e)}")
            
            # Add a small sleep to prevent high CPU usage
            self.window.after(100)
    
    def update_location(self):
        """Update location using IP-based geolocation"""
        try:
            response = requests.get("https://ipapi.co/json/")
            if response.status_code == 200:
                data = response.json()
                location = f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country_name', 'Unknown')}"
                self.location_label.configure(text=f"Location: {location}")
            else:
                self.location_label.configure(text="Location: Unable to detect")
        except Exception as e:
            logger.error(f"Error getting location: {str(e)}")
            self.location_label.configure(text="Location: Unable to detect")
    
    def handle_return(self, event):
        """Handle Enter key press"""
        if not event.state & 0x1:  # Shift is not pressed
            self.send_message()
            return 'break'
    
    def handle_shift_return(self, event):
        """Handle Shift+Enter key press"""
        return None  # Allow default behavior (new line)
    
    def send_message(self):
        """Send a message"""
        message = self.message_input.get("1.0", tk.END).strip()
        if message:
            timestamp = datetime.now().strftime("%H:%M")
            self.add_message("You", message, timestamp)
            self.message_input.delete("1.0", tk.END)
            
            try:
                # Get response from Aren's engine
                response = self.aren_engine.process_input(message)
                self.add_message("Aren", response, timestamp)
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                error_msg = "I encountered an error. Please try again. (Kuch gadbad ho gayi. Phir se koshish karein.)"
                self.add_message("Aren", error_msg, timestamp)
    
    def add_message(self, sender, message, timestamp):
        """Add a message to the chat display"""
        self.chat_display.configure(state='normal')
        
        # Add sender name with different colors
        if sender == "You":
            sender_color = "#4CAF50"  # Green
        else:
            sender_color = "#2196F3"  # Blue
            
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_display.insert(tk.END, f"{sender}: ", ("sender", sender_color))
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
        
        # Save to chat history
        self.save_message(sender, message, timestamp)
    
    def load_chat_history(self):
        """Load chat history from file"""
        try:
            if os.path.exists('chat_history.json'):
                with open('chat_history.json', 'r') as f:
                    history = json.load(f)
                    self.chat_display.configure(state='normal')
                    for msg in history:
                        self.add_message(msg['sender'], msg['message'], msg['timestamp'])
                    self.chat_display.configure(state='disabled')
        except Exception as e:
            logger.error(f"Error loading chat history: {e}")
    
    def save_message(self, sender, message, timestamp):
        """Save message to chat history"""
        try:
            history = []
            if os.path.exists('chat_history.json'):
                with open('chat_history.json', 'r') as f:
                    history = json.load(f)
            
            history.append({
                'sender': sender,
                'message': message,
                'timestamp': timestamp
            })
            
            with open('chat_history.json', 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            self.on_closing()

if __name__ == "__main__":
    app = ArenChatGUI()
    app.run() 