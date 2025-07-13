# A.R.E.N. (Assistant for Regular and Extraordinary Needs)

A powerful AI assistant that can help you with various tasks in both English and Hindi. AREN is designed to be your everyday companion for regular tasks and extraordinary needs.

## Features

### 1. Information Services
- **Time & Date**: Get current time and date information
  - "What's the current time?" / "Abhi kitne baje hain?"
  - "Today's date?" / "Aaj ki tareekh batao"

- **Weather**: Check weather conditions for any location
  - "What's the weather like in Mumbai?"
  - "Delhi ka mausam kaisa hai?"

- **Calculator**: Perform mathematical calculations
  - Basic arithmetic operations
  - Percentage calculations
  - Special functions (sqrt, sin, cos, tan)
  - "Calculate 15% of 850"
  - "24 * 7 kitna hota hai?"

- **Translation**: Translate between multiple languages
  - Supports 18 languages including:
  - English, Hindi, Spanish, French, German
  - Italian, Japanese, Korean, Chinese
  - Russian, Arabic, Bengali, Urdu
  - Punjabi, Tamil, Telugu, Marathi, Gujarati

### 2. System Automation
- **Application Launch**:
  - Open common applications (Chrome, Firefox, Notepad, Calculator)
  - "Open Chrome" / "Notepad kholo"
  - Cross-platform support (Windows, Linux, MacOS)

### 3. Interactive Features
- **Bilingual Support**:
  - Full English and Hindi language support
  - Mixed language (Hinglish) understanding

- **Smart Responses**:
  - Context-aware conversations
  - Time-based greetings
  - Personalized interactions
  - Error handling with clear messages

- **Memory & Learning**:
  - Conversation history tracking
  - User preference learning
  - Context retention between sessions

### 4. User Interface
- **Modern GUI**:
  - Dark theme interface
  - Easy-to-use chat interface
  - Message history with timestamps
  - Status indicators

- **Input Methods**:
  - Enter to send messages
  - Shift+Enter for multi-line input
  - Clear message formatting

### 5. Mobile App & API
- **Mobile Application**:
  - React Native & Expo-based mobile app
  - Voice recognition interface
  - Chat history with timestamps
  - Works on Android and iOS

- **API Server**:
  - RESTful API for mobile and web integration
  - Status and processing endpoints
  - JSON-based communication
  - Cross-platform compatibility

## Project Structure
```
aren/
├── brain/
│   ├── __init__.py
│   ├── core.py           # Core processing logic
│   ├── decision.py       # Decision making system
│   ├── engine.py         # Main AREN engine
│   └── context.py        # Context management
├── features/
│   ├── information/
│   │   ├── calculator.py     # Math calculations
│   │   ├── search.py         # Web search
│   │   ├── time_date.py      # Time and date
│   │   ├── translator.py     # Language translation
│   │   └── weather.py        # Weather information
│   ├── interaction/
│   │   ├── personality.py    # Personality traits
│   │   └── responses.py      # Response generation
│   └── actions/
│       └── automation.py     # System automation
├── utils/
│   ├── logging_utils.py      # Logging utilities
│   └── database.py          # Database management
├── logs/                    # Log files
├── memory/
│   └── user_data/          # User data storage
├── mobile/                 # Mobile app codebase
│   ├── app/                # Expo Router app directory
│   ├── components/         # React Native components
│   ├── screens/            # App screens
│   └── services/           # API services
├── api_server.py           # API server implementation
├── run_aren.py             # Multi-mode runner script
├── main.py                 # Main entry point
├── chat_gui.py             # GUI interface
└── requirements.txt        # Dependencies
```

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - PostgreSQL 13+ (for database)
   - Internet connection (for weather and translation)

2. **Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/aren.git
   cd aren

   # Install dependencies
   pip install -r requirements.txt

   # Configure database
   # Edit utils/database.py with your PostgreSQL credentials
   # See POSTGRES_MIGRATION.md for PostgreSQL setup instructions
   ```

3. **API Keys** (Optional):
   - For weather: Get OpenWeatherMap API key
   - Set in environment variables or .env file

## Running AREN

### GUI Mode (Recommended)
```bash
python main.py
```

### CLI Mode (Alternative)
```bash
python main.py --cli
```

### API Server Mode (For Mobile App)
```bash
python run_aren.py --api [port]
```

### Combined Mode (GUI + API Server)
```bash
python run_aren.py --combined [port]
```

## Mobile App Integration

The AREN mobile app connects to the backend API server to provide a voice-based interface on mobile devices.

For detailed setup instructions, see [MOBILE_INTEGRATION.md](MOBILE_INTEGRATION.md)

## Usage Tips

1. **Language**:
   - Use English, Hindi, or mix both
   - Clear pronunciation helps accuracy

2. **Commands**:
   - Be specific in requests
   - Use natural language
   - Both short and detailed commands work

3. **Features**:
   - Start with "help" to see available commands
   - Use "examples" to see usage examples

## Error Handling

- If Aren doesn't understand, it will ask for clarification
- For technical errors, check the logs/ directory
- Database errors will be reported in the status bar

## Creator

Created by Devraj Singh Shakya (Ghost/Dev)
B.Tech CSE student at Amity University Gwalior

## License

This project is licensed under the MIT License - see the LICENSE file for details.
