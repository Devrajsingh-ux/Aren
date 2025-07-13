"""
Configure Mobile App Script
This script helps users configure the mobile app to connect to the AREN API server.
"""

import os
import socket
import re
import sys

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def update_api_url(api_url):
    """Update the API URL in the mobile app configuration"""
    api_file_path = os.path.join("mobile", "services", "arenApi.ts")
    
    # Check if the file exists
    if not os.path.exists(api_file_path):
        print(f"Error: Could not find {api_file_path}")
        return False
    
    try:
        # Read the current file
        with open(api_file_path, 'r') as file:
            content = file.read()
        
        # Replace the API_BASE_URL line
        pattern = r"const API_BASE_URL = ['\"].*['\"];"
        replacement = f"const API_BASE_URL = '{api_url}';"
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            
            # Write the updated content back to the file
            with open(api_file_path, 'w') as file:
                file.write(new_content)
                
            print(f"Successfully updated API URL to: {api_url}")
            return True
        else:
            print("Error: Could not find API_BASE_URL in the file")
            return False
    except Exception as e:
        print(f"Error updating API URL: {str(e)}")
        return False

def main():
    """Main function"""
    print("AREN Mobile App Configuration Tool")
    print("==================================")
    
    # Get the local IP address
    local_ip = get_local_ip()
    
    # Default port is 5000
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            return
    
    # Suggest options for the API URL
    print("\nSelect an API URL configuration:")
    print(f"1. Local network (physical device): http://{local_ip}:{port}")
    print("2. Android emulator: http://10.0.2.2:5000")
    print("3. iOS simulator: http://localhost:5000")
    print("4. Custom URL")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        api_url = f"http://{local_ip}:{port}"
    elif choice == "2":
        api_url = "http://10.0.2.2:5000"
    elif choice == "3":
        api_url = "http://localhost:5000"
    elif choice == "4":
        api_url = input("Enter custom API URL (e.g., https://example.com:5000): ")
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Update the API URL in the mobile app configuration
    if update_api_url(api_url):
        print("\nNext steps:")
        print("1. Start the AREN API server:")
        print("   python run_aren.py --api")
        print("2. Build and run the mobile app:")
        print("   cd mobile")
        print("   npm install")
        print("   npx expo start")
    else:
        print("\nFailed to update API URL. Please check the error message above.")

if __name__ == "__main__":
    main() 