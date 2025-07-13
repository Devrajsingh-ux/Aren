# AREN Mobile Integration Guide

This guide explains how to connect the AREN mobile app with the AREN backend server.

## Setup Instructions

### 1. Start the AREN API Server

The AREN backend now includes an API server that the mobile app can connect to. To start the API server:

```bash
# Run only the API server
python run_aren.py --api [port]

# Or run both the API server and GUI
python run_aren.py --combined [port]
```

The default port is 5000 if not specified.

### 2. Configure the Mobile App

The mobile app needs to know the IP address of your AREN backend server. 

#### For Development

Edit `mobile/services/arenApi.ts` to set the correct API_BASE_URL:

- For physical devices: Use your computer's local network IP address
  ```
  const API_BASE_URL = 'http://192.168.1.100:5000';  // Replace with your computer's IP
  ```

- For Android emulator: Use 10.0.2.2 (which points to the host machine)
  ```
  const API_BASE_URL = 'http://10.0.2.2:5000';
  ```

- For iOS simulator: Use localhost
  ```
  const API_BASE_URL = 'http://localhost:5000';
  ```

#### For Production APK

When building an APK for production, you need to:

1. Host the AREN backend on a server with a public IP address or domain name
2. Update the API_BASE_URL in `mobile/services/arenApi.ts` to point to your server:
   ```
   const API_BASE_URL = 'https://your-server-domain.com';
   ```

### 3. Build the Mobile App

To build the mobile app for Android:

```bash
cd mobile
npm install
npx expo prebuild
npx expo build:android
```

## API Endpoints

The AREN API server provides the following endpoints:

- `GET /status` - Health check endpoint
- `POST /listen` - Process user input and return AREN's response
  - Request body: `{ "text": "user input", "userId": "optional_user_id" }`
  - Response: `{ "status": "success", "reply": "AREN's response", "userId": "user_id" }`

## Troubleshooting

### Mobile App Cannot Connect to API

1. Verify the API server is running by visiting `http://localhost:5000/status` in your browser
2. Check that you're using the correct IP address in the mobile app
3. Make sure your firewall allows connections to the API port
4. If using a physical device, ensure it's on the same network as your computer

### API Server Won't Start

1. Check if another process is using port 5000
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check the logs for specific error messages

## Security Considerations

For production use, consider:

1. Adding authentication to the API
2. Using HTTPS instead of HTTP
3. Implementing rate limiting
4. Securing sensitive data 