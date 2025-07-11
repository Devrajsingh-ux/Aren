import { PermissionsAndroid, Platform } from 'react-native';
import Voice, { SpeechErrorEvent, SpeechResultsEvent } from 'react-native-voice';

/**
 * Type definition for speech recognition callbacks
 */
export interface SpeechCallbacks {
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onSpeechResults?: (results: string[]) => void;
  onSpeechError?: (error: string) => void;
}

/**
 * Check if the app has microphone permissions
 * @returns Promise resolving to a boolean indicating if permission is granted
 */
export const checkMicrophonePermission = async (): Promise<boolean> => {
  try {
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
        {
          title: 'Microphone Permission',
          message: 'AREN needs access to your microphone to listen to your commands.',
          buttonPositive: 'Allow',
          buttonNegative: 'Cancel',
        }
      );
      return granted === PermissionsAndroid.RESULTS.GRANTED;
    } else {
      // iOS handles permissions differently through Info.plist
      return true;
    }
  } catch (err) {
    console.error('Permission check error:', err);
    return false;
  }
};

/**
 * Initialize speech recognition with callbacks
 * @param callbacks Object containing callback functions for speech events
 */
export const initSpeechRecognition = (callbacks: SpeechCallbacks): void => {
  // Set up Voice listeners
  Voice.onSpeechStart = callbacks.onSpeechStart || (() => {});
  Voice.onSpeechEnd = callbacks.onSpeechEnd || (() => {});
  
  Voice.onSpeechResults = (e: SpeechResultsEvent) => {
    if (callbacks.onSpeechResults && e.value) {
      callbacks.onSpeechResults(e.value);
    }
  };
  
  Voice.onSpeechError = (e: SpeechErrorEvent) => {
    if (callbacks.onSpeechError) {
      callbacks.onSpeechError(e.error?.message || 'Unknown error');
    }
  };
};

/**
 * Start speech recognition
 * @param locale Language locale (default: 'en-US')
 */
export const startListening = async (locale: string = 'en-US'): Promise<void> => {
  try {
    await Voice.start(locale);
  } catch (e) {
    console.error('Failed to start speech recognition:', e);
    throw e;
  }
};

/**
 * Stop speech recognition
 */
export const stopListening = async (): Promise<void> => {
  try {
    await Voice.stop();
  } catch (e) {
    console.error('Failed to stop speech recognition:', e);
    throw e;
  }
};

/**
 * Clean up speech recognition resources
 */
export const destroySpeechRecognition = async (): Promise<void> => {
  try {
    await Voice.destroy();
    Voice.removeAllListeners();
  } catch (e) {
    console.error('Failed to destroy speech recognition:', e);
  }
}; 