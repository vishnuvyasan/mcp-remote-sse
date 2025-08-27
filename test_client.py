import requests
import json
import time
import sseclient
import threading
import sys

# Configuration
BASE_URL = "http://localhost:8001"
CLIENT_ID = "example_client_id"
CLIENT_SECRET = "example_client_secret"

def get_token():
    """Get OAuth token using client credentials"""
    token_url = f"{BASE_URL}/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "calculator sse"
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token: {response.text}")
        sys.exit(1)

def test_calculator(token):
    """Test calculator endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test addition
    response = requests.post(f"{BASE_URL}/calculator/add?a=5&b=3", headers=headers)
    print(f"Addition result: {response.json()}")
    
    # Test subtraction
    response = requests.post(f"{BASE_URL}/calculator/subtract?a=10&b=4", headers=headers)
    print(f"Subtraction result: {response.json()}")
    
    # Test multiplication
    response = requests.post(f"{BASE_URL}/calculator/multiply?a=6&b=7", headers=headers)
    print(f"Multiplication result: {response.json()}")
    
    # Test division
    response = requests.post(f"{BASE_URL}/calculator/divide?a=20&b=5", headers=headers)
    print(f"Division result: {response.json()}")
    
    # Test division by zero (should fail)
    try:
        response = requests.post(f"{BASE_URL}/calculator/divide?a=20&b=0", headers=headers)
        print(f"Division by zero result: {response.json()}")
    except Exception as e:
        print(f"Division by zero correctly failed: {e}")

def sse_listener(token):
    """Listen for SSE events"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/events", headers=headers, stream=True)
        client = sseclient.SSEClient(response)
        
        print("SSE connection established. Waiting for messages...")
        for event in client.events():
            print(f"Received SSE message: {event.data}")
    except Exception as e:
        print(f"SSE connection error: {e}")

def broadcast_message(token, message):
    """Broadcast a message to all SSE clients"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/broadcast?message={message}", headers=headers)
    print(f"Broadcast response: {response.json()}")

def main():
    print("Starting MCP client test...")
    
    # Get OAuth token
    token = get_token()
    print(f"Obtained token: {token[:10]}...")
    
    # Start SSE listener in a separate thread
    sse_thread = threading.Thread(target=sse_listener, args=(token,))
    sse_thread.daemon = True
    sse_thread.start()
    
    # Wait for SSE connection to establish
    time.sleep(2)
    
    # Test calculator endpoints
    test_calculator(token)
    
    # Broadcast a message
    broadcast_message(token, "Hello from test client!")
    
    # Keep the main thread alive for a while to receive SSE messages
    time.sleep(5)
    
    print("Test completed.")

if __name__ == "__main__":
    main()

# Made with Bob
