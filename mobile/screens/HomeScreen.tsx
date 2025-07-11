import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useRef, useState } from 'react';
import {
    AppState,
    AppStateStatus,
    KeyboardAvoidingView,
    Platform,
    SafeAreaView,
    ScrollView,
    StatusBar,
    StyleSheet,
    Text,
    View
} from 'react-native';
import VoiceBar from '../components/VoiceBar';
import { checkApiStatus, sendUserMessage } from '../services/arenApi';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const HomeScreen: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isApiConnected, setIsApiConnected] = useState<boolean>(true);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const appState = useRef(AppState.currentState);

  useEffect(() => {
    // Check API connection on component mount
    checkConnection();
    
    // Set up app state change listener to check connection when app comes to foreground
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    
    return () => {
      subscription.remove();
    };
  }, []);
  
  const handleAppStateChange = (nextAppState: AppStateStatus) => {
    if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
      // App has come to the foreground, check connection
      checkConnection();
    }
    appState.current = nextAppState;
  };

  const checkConnection = async () => {
    try {
      const isConnected = await checkApiStatus();
      setIsApiConnected(isConnected);
      
      // Add welcome message if API is connected and no messages exist
      if (messages.length === 0) {
        if (isConnected) {
          addMessage('Hi, I\'m AREN. How can I help you today?', false);
        } else {
          addMessage('I\'m having trouble connecting to my brain. I\'ll operate in offline mode for now.', false);
        }
      } else if (!isConnected && isApiConnected) {
        // If we just lost connection and had it before, add a message
        addMessage('I\'ve lost connection to my brain. I\'ll operate in offline mode for now.', false);
      } else if (isConnected && !isApiConnected) {
        // If we just regained connection and didn't have it before, add a message
        addMessage('I\'m back online! How can I help you?', false);
      }
    } catch (error) {
      console.error('Connection check error:', error);
      setIsApiConnected(false);
      
      if (messages.length === 0) {
        addMessage('I\'m having trouble connecting to my brain. I\'ll operate in offline mode for now.', false);
      }
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollViewRef.current && messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const addMessage = (text: string, isUser: boolean) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser,
      timestamp: new Date(),
    };
    
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  };

  const handleMessageReceived = async (message: string) => {
    // Add the user's message
    addMessage(message, true);
    
    // Don't send duplicate requests if already processing
    if (isProcessing) return;
    
    try {
      setIsProcessing(true);
      
      // Get response from AREN
      const response = await sendUserMessage(message);
      
      // Add AREN's response after a small delay for better UX
      setTimeout(() => {
        addMessage(response, false);
        setIsProcessing(false);
      }, 500);
      
    } catch (error) {
      console.error('Error processing message:', error);
      
      // Add error message
      setTimeout(() => {
        addMessage("I'm sorry, I couldn't process your request right now.", false);
        setIsProcessing(false);
      }, 500);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" />
      <View style={styles.container}>
        <LinearGradient
          colors={['#121212', '#1E1E1E']}
          style={styles.gradientBackground}
        />
        <View style={styles.header}>
          <Text style={styles.headerTitle}>
            AREN {!isApiConnected && <Text style={styles.offlineIndicator}>(Offline)</Text>}
            {isProcessing && <Text style={styles.processingIndicator}> (Thinking...)</Text>}
          </Text>
        </View>

        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardAvoidingView}
        >
          <ScrollView
            ref={scrollViewRef}
            style={styles.messagesContainer}
            contentContainerStyle={styles.messagesContent}
          >
            {messages.map((msg) => (
              <View
                key={msg.id}
                style={[
                  styles.messageBubble,
                  msg.isUser ? styles.userMessage : styles.arenMessage,
                ]}
              >
                <Text style={styles.messageText}>{msg.text}</Text>
                <Text style={styles.timestamp}>
                  {msg.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Text>
              </View>
            ))}
          </ScrollView>

          {!isApiConnected && (
            <View style={styles.offlineWarning}>
              <Text style={styles.offlineText}>
                Operating in offline mode. Responses are simulated.
              </Text>
            </View>
          )}

          <VoiceBar onMessageReceived={handleMessageReceived} />
        </KeyboardAvoidingView>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#121212',
  },
  container: {
    flex: 1,
    position: 'relative',
  },
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  header: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  offlineIndicator: {
    fontSize: 14,
    color: '#ff5555',
    fontWeight: 'normal',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
    paddingHorizontal: 15,
  },
  messagesContent: {
    paddingTop: 10,
    paddingBottom: 100, // Space for the voice bar
  },
  messageBubble: {
    padding: 12,
    borderRadius: 18,
    marginVertical: 5,
    maxWidth: '80%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1,
    elevation: 2,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#4A6FFF',
    borderBottomRightRadius: 5,
  },
  arenMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#333',
    borderBottomLeftRadius: 5,
  },
  messageText: {
    color: '#fff',
    fontSize: 16,
  },
  timestamp: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.6)',
    alignSelf: 'flex-end',
    marginTop: 5,
  },
  offlineWarning: {
    backgroundColor: 'rgba(255, 0, 0, 0.1)',
    padding: 8,
    margin: 10,
    borderRadius: 5,
    borderWidth: 1,
    borderColor: 'rgba(255, 0, 0, 0.3)',
  },
  offlineText: {
    color: '#ff5555',
    textAlign: 'center',
    fontSize: 12,
  },
  processingIndicator: {
    fontSize: 14,
    color: '#2575FC',
    fontWeight: 'normal',
  },
});

export default HomeScreen; 