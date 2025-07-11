"""
Test script for AREN API Server
This script tests the API endpoints to ensure they are working correctly.
"""

import requests
import json
import sys
import socket

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

def test_status(base_url):
    """Test the status endpoint"""
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        print(f"Status Endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing status endpoint: {str(e)}")
        return False

def test_listen(base_url, query="Hello, how are you?"):
    """Test the listen endpoint"""
    try:
        data = {
            "text": query,
            "userId": "test_user"
        }
        response = requests.post(
            f"{base_url}/listen", 
            json=data,
            timeout=10
        )
        print(f"Listen Endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing listen endpoint: {str(e)}")
        return False

def main():
    """Main function"""
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
    
    # Base URL for API
    base_url = f"http://{local_ip}:{port}"
    print(f"Testing API at {base_url}")
    
    # Test endpoints
    status_ok = test_status(base_url)
    if status_ok:
        print("\nStatus endpoint is working!")
    else:
        print("\nStatus endpoint failed!")
        return
    
    listen_ok = test_listen(base_url)
    if listen_ok:
        print("\nListen endpoint is working!")
    else:
        print("\nListen endpoint failed!")
        return
    
    print("\nAll tests passed! The API server is working correctly.")
    print(f"\nYou can use this URL in your mobile app:")
    print(f"API_BASE_URL = '{base_url}';")

if __name__ == "__main__":
    main() 