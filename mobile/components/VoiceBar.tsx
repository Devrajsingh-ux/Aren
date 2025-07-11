import { FontAwesome, MaterialIcons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import * as Speech from 'expo-speech';
import React, { useEffect, useState } from 'react';
import {
  Animated,
  PermissionsAndroid,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from 'react-native';
import Voice from 'react-native-voice';
import SimpleAudioVisualizer from './SimpleAudioVisualizer';

interface VoiceBarProps {
  onMessageReceived: (message: string) => void;
}

const VoiceBar: React.FC<VoiceBarProps> = ({ onMessageReceived }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [textInput, setTextInput] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [voiceModuleAvailable, setVoiceModuleAvailable] = useState(true);
  
  // Animation value for the mic button
  const pulseAnim = new Animated.Value(1);

  useEffect(() => {
    // Check if Voice module is properly initialized
    try {
      // Set up Voice listeners
      if (Voice) {
        Voice.onSpeechStart = () => setIsListening(true);
        Voice.onSpeechEnd = () => setIsListening(false);
        Voice.onSpeechResults = (e) => {
          if (e.value && e.value[0]) {
            setTranscript(e.value[0]);
          }
        };
        Voice.onSpeechError = (e) => {
          setError(e.error?.message || 'Something went wrong');
          setIsListening(false);
        };

        // Request microphone permission
        checkPermission();
      } else {
        setVoiceModuleAvailable(false);
        setError('Voice recognition not available');
      }
    } catch (err) {
      console.error('Voice module initialization error:', err);
      setVoiceModuleAvailable(false);
      setError('Voice recognition not available');
    }

    // Clean up listeners
    return () => {
      try {
        if (Voice && Voice.destroy) {
          Voice.destroy().then(Voice.removeAllListeners);
        }
        Speech.stop();
      } catch (err) {
        console.error('Error cleaning up voice module:', err);
      }
    };
  }, []);

  // Animation effect when listening
  useEffect(() => {
    if (isListening) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      Animated.timing(pulseAnim, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [isListening]);

  const checkPermission = async () => {
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
        setHasPermission(granted === PermissionsAndroid.RESULTS.GRANTED);
      } else {
        // iOS handles permissions differently
        setHasPermission(true);
      }
    } catch (err) {
      console.error('Permission check error:', err);
      setHasPermission(false);
    }
  };

  const handleSendText = () => {
    if (!textInput.trim()) return;
    
    // Send the message to parent component
    onMessageReceived(textInput);
    
    // Clear the input
    setTextInput('');
  };

  const toggleListening = async () => {
    try {
      if (!voiceModuleAvailable) {
        setError('Voice recognition is not available on this device');
        // Simulate a response for demo purposes
        setTimeout(() => {
          onMessageReceived("I'm sorry, voice recognition isn't available. This is a simulated response.");
        }, 1000);
        return;
      }

      if (!hasPermission) {
        await checkPermission();
        return;
      }

      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      
      if (isListening) {
        try {
          await Voice.stop();
          setIsListening(false);
          
          // If we have a transcript, send it to the parent component
          if (transcript) {
            onMessageReceived(transcript);
            setTranscript('');
          }
        } catch (voiceError) {
          console.error('Voice stop error:', voiceError);
          setIsListening(false);
        }
      } else {
        setTranscript('');
        setError(null);
        try {
          if (Voice && Voice.start) {
            await Voice.start('en-US');
          } else {
            throw new Error('Voice module not properly initialized');
          }
        } catch (startError) {
          console.error('Voice start error:', startError);
          setError('Could not start voice recognition');
          setIsListening(false);
        }
      }
    } catch (e) {
      console.error('Toggle listening error:', e);
      setError('Failed to start voice recognition');
    }
  };

  const toggleSpeaking = () => {
    setIsSpeaking(!isSpeaking);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  // Fallback function for demo purposes when voice module isn't available
  const simulateVoiceInput = () => {
    if (!voiceModuleAvailable) {
      setIsListening(true);
      setTranscript('This is a simulated voice input for demo purposes');
      
      setTimeout(() => {
        setIsListening(false);
        onMessageReceived("This is a simulated voice input for demo purposes");
      }, 2000);
    }
  };

  return (
    <View style={styles.container}>
      {/* Live transcription */}
      {isListening && (
        <View style={styles.transcriptContainer}>
          <Text style={styles.transcriptText}>
            {transcript || "Listening..."}
          </Text>
          <SimpleAudioVisualizer 
            style={styles.visualizer}
            isActive={isListening}
            colors={['#6A11CB', '#2575FC']}
          />
        </View>
      )}
      
      {/* Error message */}
      {error && !isListening && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      
      {/* Voice bar */}
      <BlurView intensity={30} style={styles.blurContainer}>
        <View style={styles.voiceBar}>
          <TextInput
            style={styles.textInput}
            placeholder="Type a message..."
            placeholderTextColor="#aaa"
            value={textInput}
            onChangeText={setTextInput}
            onSubmitEditing={handleSendText}
            returnKeyType="send"
          />
          
          <View style={styles.buttonsContainer}>
            <TouchableOpacity 
              style={styles.sendButton}
              onPress={handleSendText}
              disabled={!textInput.trim()}
            >
              <MaterialIcons 
                name="send" 
                size={22} 
                color={textInput.trim() ? "#2575FC" : "#555"}
              />
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.speakerButton} 
              onPress={toggleSpeaking}
            >
              <MaterialIcons 
                name={isSpeaking ? "volume-up" : "volume-off"} 
                size={22} 
                color={isSpeaking ? "#2575FC" : "#888"}
              />
            </TouchableOpacity>
            
            <Animated.View
              style={[
                styles.micButtonContainer,
                {
                  transform: [{ scale: pulseAnim }],
                  backgroundColor: isListening ? '#6A11CB' : '#333',
                },
              ]}
            >
              <TouchableOpacity
                style={styles.micButton}
                onPress={voiceModuleAvailable ? toggleListening : simulateVoiceInput}
                disabled={hasPermission === false}
              >
                <FontAwesome
                  name="microphone"
                  size={24}
                  color={isListening ? '#fff' : '#ddd'}
                />
              </TouchableOpacity>
            </Animated.View>
          </View>
        </View>
      </BlurView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 30,
    left: 20,
    right: 20,
    alignItems: 'center',
  },
  blurContainer: {
    width: '100%',
    borderRadius: 30,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  voiceBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 20,
    backgroundColor: 'rgba(30, 30, 30, 0.7)',
  },
  textInput: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    paddingVertical: 8,
    paddingHorizontal: 0,
  },
  placeholder: {
    color: '#aaa',
    fontSize: 16,
    flex: 1,
  },
  buttonsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sendButton: {
    marginRight: 15,
    padding: 5,
  },
  speakerButton: {
    marginRight: 15,
    padding: 5,
  },
  micButtonContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#6A11CB',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  micButton: {
    width: '100%',
    height: '100%',
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  transcriptContainer: {
    backgroundColor: 'rgba(30, 30, 30, 0.8)',
    padding: 15,
    borderRadius: 15,
    marginBottom: 15,
    width: '100%',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  transcriptText: {
    color: 'white',
    fontSize: 16,
  },
  visualizer: {
    height: 30,
    marginTop: 10,
  },
  errorContainer: {
    backgroundColor: 'rgba(255, 50, 50, 0.2)',
    padding: 10,
    borderRadius: 10,
    marginBottom: 10,
    width: '100%',
  },
  errorText: {
    color: '#ff5555',
    fontSize: 14,
  },
});

export default VoiceBar; 