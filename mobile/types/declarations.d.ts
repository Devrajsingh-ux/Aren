// Type declarations for modules without type definitions

declare module 'react-native-voice' {
  export interface SpeechResultsEvent {
    value?: string[];
  }
  
  export interface SpeechErrorEvent {
    error?: {
      message?: string;
    };
  }
  
  interface Voice {
    onSpeechStart: (() => void) | null;
    onSpeechEnd: (() => void) | null;
    onSpeechResults: ((e: SpeechResultsEvent) => void) | null;
    onSpeechError: ((e: SpeechErrorEvent) => void) | null;
    
    start: (locale?: string) => Promise<void>;
    stop: () => Promise<void>;
    destroy: () => Promise<void>;
    removeAllListeners: () => void;
    isAvailable?: () => Promise<boolean>;
  }
  
  const Voice: Voice;
  export default Voice;
}

declare module 'expo-linear-gradient' {
  import React from 'react';
  import { ViewStyle } from 'react-native';
  
  interface LinearGradientProps {
    colors: string[];
    style?: ViewStyle;
    start?: { x: number; y: number };
    end?: { x: number; y: number };
    children?: React.ReactNode;
  }
  
  export const LinearGradient: React.FC<LinearGradientProps>;
}

declare module '../services/arenApi' {
  export function sendAudioTranscription(text: string): Promise<string>;
  export function checkApiStatus(): Promise<boolean>;
} 