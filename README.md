# A.R.E.N - Autonomous Responsive Enhanced Nexus

A.R.E.N is an advanced AI assistant designed to provide intelligent responses and perform various tasks through natural language processing.

## Features

- Natural language understanding and processing
- Web search capabilities
- Application launching
- Time and date information
- Personality and conversational abilities
- GUI interface with chat history
- Theme customization
- Emoji support

## Requirements

- Python 3.8 or higher
- Windows operating system
- Internet connection (for web search functionality)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aren.git
   cd aren
   ```

2. Run the setup script:
   ```bash
   run_aren.bat
   ```

This will:
- Create a virtual environment
- Install all required dependencies
- Start A.R.E.N

## Usage

### GUI Mode
Simply run the application and use the graphical interface to interact with A.R.E.N.

### Console Mode
Run the application with the `--console` flag:
```bash
python main.py --console
```

## Available Commands

- Ask for time/date
- Search the web
- Set reminders
- Launch applications
- Have casual conversations
- Ask about A.R.E.N's identity
- Request jokes or motivation
- Get weather reactions

## Project Structure

```
aren/
├── brain/
│   └── processor.py      # Neural processing and text analysis
├── features/
│   └── command_processor.py  # Command handling and features
├── gui/
│   └── main_window.py    # GUI implementation
├── main.py              # Main entry point
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Development

### Adding New Features

1. Add new command handlers in `features/command_processor.py`
2. Update the neural processing in `brain/processor.py`
3. Modify the GUI in `gui/main_window.py` if needed

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt team for the GUI framework
- Python community for various libraries and tools

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 