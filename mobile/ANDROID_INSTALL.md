# Installing AREN on Your Android Device

## Method 1: Using Expo Go (Easiest)

This method allows you to install and run the AREN assistant directly on your Android device without building an APK:

1. **Install Expo Go app** on your Android device:
   - Download from [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - Open the Expo Go app after installation

2. **Start the development server** on your computer:
   ```bash
   npx expo start
   ```

3. **Connect your Android device**:
   - Make sure your Android device and computer are on the same WiFi network
   - Open the Expo Go app on your Android device
   - Tap "Scan QR Code" and scan the QR code shown in your terminal
   - OR tap "Enter URL manually" and enter the URL shown in your terminal

4. The AREN app will load and run on your Android device through Expo Go

## Method 2: Using Expo Go with Tunnel Connection

If you're having trouble connecting to the development server, try using a tunnel connection:

1. **Start the development server with tunnel option**:
   ```bash
   npx expo start --tunnel
   ```

2. Wait for the tunnel to be established (this may take a minute)

3. **Connect your Android device**:
   - Open the Expo Go app on your Android device
   - Scan the new QR code that appears in your terminal
   - The app will load through an internet connection rather than local WiFi

## Method 3: Build a Development APK

If you want to build a standalone APK for development:

1. **Create an Expo account** at [expo.dev](https://expo.dev)

2. **Install EAS CLI**:
   ```bash
   npm install -g eas-cli
   ```

3. **Log in to your Expo account**:
   ```bash
   eas login
   ```

4. **Configure the build**:
   ```bash
   eas build:configure
   ```

5. **Build the APK**:
   ```bash
   eas build -p android --profile development
   ```

6. **Download and install the APK** on your Android device

## Troubleshooting

### Common Issues:

1. **QR code not scanning**:
   - Make sure your device and computer are on the same network
   - Try using the tunnel option with `npx expo start --tunnel`
   - Try entering the URL manually in Expo Go

2. **Voice recognition not working**:
   - Make sure you've granted microphone permissions
   - Check that you're in a quiet environment
   - The app has fallback mechanisms for when voice recognition isn't available

3. **App crashes on startup**:
   - Make sure you have the latest version of Expo Go
   - Try clearing the Expo Go app cache
   - Restart your Android device

4. **API connection issues**:
   - The app will automatically switch to offline mode with simulated responses
   - Check your internet connection
   - Verify the API endpoint in services/arenApi.ts 