import React, { useEffect, useState } from 'react';
import { Animated, StyleSheet, View } from 'react-native';

interface SimpleAudioVisualizerProps {
  isActive: boolean;
  colors: string[];
  style?: any;
}

const SimpleAudioVisualizer: React.FC<SimpleAudioVisualizerProps> = ({ isActive, colors, style }) => {
  const [bars] = useState(Array(10).fill(0).map(() => new Animated.Value(0)));
  const primaryColor = colors[0] || '#6A11CB';
  const secondaryColor = colors[1] || '#2575FC';
  
  useEffect(() => {
    if (isActive) {
      // Animate each bar with random heights and durations
      bars.forEach((bar, index) => {
        animateBar(bar, index);
      });
    } else {
      // Reset all bars when not active
      bars.forEach(bar => {
        Animated.timing(bar, {
          toValue: 0,
          duration: 300,
          useNativeDriver: false,
        }).start();
      });
    }
  }, [isActive]);

  const animateBar = (bar: Animated.Value, index: number) => {
    const randomHeight = Math.random() * 0.8 + 0.2; // Between 0.2 and 1
    const randomDuration = Math.random() * 300 + 500; // Between 500ms and 800ms
    
    Animated.sequence([
      Animated.timing(bar, {
        toValue: randomHeight,
        duration: randomDuration,
        useNativeDriver: false,
      }),
      Animated.timing(bar, {
        toValue: Math.random() * 0.5 + 0.2,
        duration: randomDuration * 0.8,
        useNativeDriver: false,
      })
    ]).start(() => {
      if (isActive) {
        animateBar(bar, index);
      }
    });
  };

  return (
    <View style={[styles.container, style]}>
      {bars.map((bar, index) => (
        <Animated.View
          key={index}
          style={[
            styles.bar,
            {
              backgroundColor: index % 2 === 0 ? primaryColor : secondaryColor,
              height: bar.interpolate({
                inputRange: [0, 1],
                outputRange: ['0%', '100%']
              }),
            }
          ]}
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 30,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 5,
  },
  bar: {
    width: 4,
    borderRadius: 2,
    backgroundColor: '#6A11CB',
  },
});

export default SimpleAudioVisualizer; 