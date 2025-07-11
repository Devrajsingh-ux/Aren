import axios from 'axios';

// Base URL for the API
// For development on physical devices, use your computer's local network IP address
// Example: 'http://192.168.1.100:5000' 
// For Android emulator, use 'http://10.0.2.2:5000'
// For iOS simulator, use 'http://localhost:5000'
const API_BASE_URL = 'http://10.0.2.2:5000'; // Default for Android emulator

// Set a timeout for API requests
axios.defaults.timeout = 10000; // 10 seconds for mobile networks

// Flag to enable mock responses when API is unavailable
const USE_MOCK_RESPONSES = true;

// Mock responses for demo purposes when API is unavailable
const MOCK_RESPONSES = [
  "I'm here to help you. What would you like to know?",
  "That's an interesting question. Let me think about it.",
  "I understand what you're asking. Here's what I know.",
  "I'm AREN, your personal AI assistant.",
  "I can help you with information, tasks, and more.",
  "That's a good point. Let me elaborate on that.",
];

// Get a random mock response
const getRandomMockResponse = (): string => {
  const index = Math.floor(Math.random() * MOCK_RESPONSES.length);
  return MOCK_RESPONSES[index];
};

/**
 * Send user input to the API for processing
 * Works with both text and voice input
 * @param text The user's input text
 * @returns The response from the AI assistant
 */
export const sendAudioTranscription = async (text: string): Promise<string> => {
  try {
    // First check if API is available
    const isAvailable = await checkApiStatus();
    
    if (!isAvailable && USE_MOCK_RESPONSES) {
      console.log('API unavailable, using mock response');
      return getRandomMockResponse();
    }
    
    console.log('Sending to API:', text);
    
    const response = await axios.post(`${API_BASE_URL}/listen`, {
      text,
      userId: 'user123', // You can implement user identification as needed
    });
    
    console.log('API response:', response.data);
    
    if (response.data && response.data.reply) {
      return response.data.reply;
    }
    
    return 'I didn\'t understand that. Could you try again?';
  } catch (error) {
    console.error('API Error:', error);
    
    // Return mock response if enabled
    if (USE_MOCK_RESPONSES) {
      return getRandomMockResponse();
    }
    
    return 'Sorry, I\'m having trouble connecting to my brain right now.';
  }
};

// Alias for better naming convention
export const sendUserMessage = sendAudioTranscription;

/**
 * Check if the API is available
 * @returns Boolean indicating if the API is reachable
 */
export const checkApiStatus = async (): Promise<boolean> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/status`, {
      timeout: 2000, // Shorter timeout for status check
    });
    return response.status === 200;
  } catch (error) {
    console.error('API Status Check Error:', error);
    return false;
  }
}; 