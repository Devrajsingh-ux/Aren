# A.R.E.N. (Assistant for Regular and Extraordinary Needs)

AREN is a Python-based AI assistant designed to help with various tasks. It uses a modular architecture with a decision-making engine to process user requests and provide helpful responses.

## Features

AREN includes the following capabilities:

- **Basic Interaction**
  - Greetings and identity information
  - Jokes and casual conversation
  
- **Information Services**
  - Current time and date information
  - Web search for information
  - Weather information for locations
  - Calculator for mathematical expressions
  - Translation between multiple languages
  
- **System Actions**
  - Application launching

## Architecture

AREN is built with a modular design:

- **Brain**: Core decision-making and context management
  - Engine: Main processing logic and capability integration
  - Decision Maker: Intelligent selection of appropriate actions
  - Context Manager: Maintains conversation history and user preferences
  
- **Features**: Specialized capabilities for different tasks
  - Information: Time, date, search, weather, calculation, translation
  - Actions: Application automation
  - Interaction: Personality, greetings, identity
  
- **Memory**: Storage for user data and preferences
  - User preferences are saved between sessions
  
- **Utils**: Helper functions and utilities

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up API keys as environment variables (optional):
   - `OPENWEATHER_API_KEY` for weather functionality

## Usage

Run AREN from the command line:

```
python -m main
```

Interact with AREN by typing your queries. Some examples:

- "What time is it?"
- "Tell me a joke"
- "What's the weather in New York?"
- "Calculate 25 * 48"
- "Translate hello to Spanish"
- "Search for recent news"
- "Open notepad"

Type 'exit', 'quit', or 'bye' to end the session.

## Extending AREN

AREN is designed to be easily extended with new capabilities. To add a new feature:

1. Create a new module in the appropriate features directory
2. Implement the core functionality
3. Add detection patterns to the engine.py file
4. Register the new capability in the ArenEngine's capabilities dictionary

## License

This project is open source and available under the MIT License.
