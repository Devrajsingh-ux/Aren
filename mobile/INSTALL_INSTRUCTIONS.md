# Installing AREN on Your Device

There are several ways to install the AREN voice assistant app on your device:

## Method 1: Using Expo Go (Easiest)

1. Install the Expo Go app on your device:
   - [Android Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)

2. Start the development server (if not already running):
   ```bash
   npx expo start
   ```

3. Scan the QR code with your device:
   - Android: Use the Expo Go app to scan
   - iOS: Use the Camera app to scan

4. The app will open in Expo Go on your device

## Method 2: Development Build

This method creates a standalone app that you can install directly on your device.

### For Android:

1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   ```

2. Log in to your Expo account:
   ```bash
   eas login
   ```

3. Build a development client:
   ```bash
   eas build --profile development --platform android
   ```

4. Once the build is complete, download the APK file from the provided URL

5. Transfer the APK to your Android device and install it

### For iOS:

1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   ```

2. Log in to your Expo account:
   ```bash
   eas login
   ```

3. Build a development client:
   ```bash
   eas build --profile development --platform ios
   ```

4. Once the build is complete, you'll need to install it using TestFlight or a similar service

## Quick Install for Testing

For the fastest way to test the app:

1. Make sure your device is on the same Wi-Fi network as your development computer

2. Start the Expo development server:
   ```bash
   npx expo start
   ```

3. On Android:
   - Open the Expo Go app
   - Tap on "Scan QR Code" and scan the QR code shown in your terminal
   - OR tap on "Enter URL manually" and enter the URL shown in your terminal

4. On iOS:
   - Open the Camera app
   - Scan the QR code shown in your terminal
   - Tap the notification that appears to open in Expo Go

5. The app will load in development mode, allowing you to test all features

## Troubleshooting

### Common Issues:

1. **QR code not scanning**:
   - Make sure your device and computer are on the same network
   - Try entering the URL manually in Expo Go
   - Try using `npx expo start --tunnel` to use a tunnel connection

2. **Voice recognition not working**:
   - Make sure you've granted microphone permissions
   - Check that you're in a quiet environment
   - The app has fallback mechanisms for when voice recognition isn't available

3. **API connection issues**:
   - The app will automatically switch to offline mode with simulated responses
   - Check your internet connection
   - Verify the API endpoint in services/arenApi.ts

4. **Build errors**:
   - Make sure all dependencies are installed: `npm install`
   - Clear cache if needed: `npx expo start --clear`
   - Check for any linter errors: `npx eslint .`

For more help, refer to the [Expo documentation](https://docs.expo.dev/) or open an issue in the project repository. 