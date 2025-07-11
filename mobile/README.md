# AREN - Voice Assistant Mobile App

A Gemini-style mobile voice assistant built with React Native and Expo.

## Features

- 🎙️ Voice recognition using react-native-voice
- 💬 Chat-like interface for conversations
- 🔊 Text-to-speech for spoken responses
- 🌊 Custom audio visualization during voice input
- 🎨 Modern dark UI inspired by Google Assistant/Gemini
- 🔌 Offline mode with simulated responses when API is unavailable
- 🛡️ Robust error handling for voice recognition and API issues

## Getting Started

### Prerequisites

- Node.js (v14 or newer)
- npm or yarn
- Expo CLI
- iOS/Android development environment

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd mobile
```

2. Install dependencies
```bash
npm install
# or
yarn install
```

3. Start the Expo development server
```bash
npm start
# or
yarn start
```

4. Open the app on your device using Expo Go or run on a simulator

### Backend API

The app expects a backend API with the following endpoints:
- `POST /listen` - Processes voice commands and returns responses
- `GET /status` - Health check endpoint

Configure the API URL in `services/arenApi.ts`.

#### Offline Mode

The app includes an offline mode that provides simulated responses when the API is unavailable. This ensures the app remains functional even without backend connectivity.

To configure offline mode:
- Edit `USE_MOCK_RESPONSES` flag in `services/arenApi.ts`
- Customize mock responses in the `MOCK_RESPONSES` array

## Usage

1. Tap the microphone button to start listening
2. Speak your command or question
3. The app will transcribe your speech in real-time
4. When you finish speaking, the app will send your command to the API
5. AREN will respond with a text message (and optionally speak the response)

## Project Structure

- `app/` - Main app screens using Expo Router
- `components/` - Reusable UI components
  - `VoiceBar.tsx` - The Gemini-style floating voice input bar
  - `SimpleAudioVisualizer.tsx` - Custom audio visualization component
- `screens/` - App screens
  - `HomeScreen.tsx` - Main assistant screen
- `services/` - API and other services
  - `arenApi.ts` - API client for the backend
- `utils/` - Utility functions
  - `speech.ts` - Speech recognition utilities
- `types/` - TypeScript type definitions

## Customization

- Change the colors in the component styles to match your brand
- Modify the welcome message in `HomeScreen.tsx`
- Adjust the API endpoint in `services/arenApi.ts`
- Customize mock responses for offline mode

## Troubleshooting

### Voice Recognition Issues
- Make sure microphone permissions are granted
- Check that `react-native-voice` is properly installed
- The app includes fallbacks for when voice recognition is unavailable

### API Connection Issues
- Verify the API endpoint in `services/arenApi.ts`
- The app will automatically switch to offline mode when the API is unreachable
- Check network connectivity on your device

## License

This project is licensed under the MIT License - see the LICENSE file for details.
