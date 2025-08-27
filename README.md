# MCP Server with OAuth and SSE

A Machine Communication Protocol (MCP) server implemented in Python using FastAPI, featuring calculator tools, OAuth 2.0 client credentials authentication, and Server-Sent Events (SSE) for real-time communication.

## Features

- **OAuth 2.0 Authentication**: Secure API access using client credentials flow
- **Calculator API**: Basic arithmetic operations (add, subtract, multiply, divide)
- **Server-Sent Events**: Real-time communication from server to clients
- **FastAPI Framework**: High-performance, easy-to-use API framework
- **uv Package Manager**: Fast, reliable Python package management

## Requirements

- Python 3.8+
- uv package manager

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp_client_creds_sse
   ```

2. Run the setup script:
   
   **On Linux/macOS:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   **On Windows:**
   ```bash
   setup.bat
   ```
   
   This will:
   - Create a virtual environment
   - Activate the virtual environment
   - Install all required dependencies

3. Create a `.env` file based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your configuration settings.

## Project Structure

```
mcp_client_creds_sse/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oauth.py
│   │   └── routes.py
│   ├── calculator/
│   │   ├── __init__.py
│   │   └── calculator.py
│   └── sse/
│       ├── __init__.py
│       └── sse_manager.py
├── requirements.txt
├── run.py
├── setup.sh
├── setup.bat
├── test_client.py
└── README.md
```

## Usage

### Starting the Server

Run the server with:

```bash
# Using the run.py script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Authentication

To obtain an access token:

```bash
curl -X POST http://localhost:8001/token \
  -d "grant_type=client_credentials&client_id=example_client_id&client_secret=example_client_secret&scope=calculator+sse"
```

### Using the Calculator API

With the obtained token:

```bash
# Addition
curl -X POST "http://localhost:8001/calculator/add?a=5&b=3" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Subtraction
curl -X POST "http://localhost:8001/calculator/subtract?a=10&b=4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Multiplication
curl -X POST "http://localhost:8001/calculator/multiply?a=6&b=7" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Division
curl -X POST "http://localhost:8001/calculator/divide?a=20&b=5" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Server-Sent Events

To connect to the SSE endpoint:

```javascript
// JavaScript client example
const eventSource = new EventSource('http://localhost:8001/events', {
  headers: {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
  }
});

eventSource.onmessage = (event) => {
  console.log('Received message:', event.data);
};

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

To broadcast a message to all connected clients:

```bash
curl -X POST "http://localhost:8001/broadcast?message=Hello%20World" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Testing the Implementation

Run the test client to verify the implementation:

```bash
python test_client.py
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Implementation Notes

### OAuth 2.0 Client Credentials Flow

This project implements a custom OAuth 2.0 client credentials flow using FastAPI's security features. Since FastAPI doesn't provide a built-in `OAuth2ClientCredentialsRequestForm`, we've implemented our own version that:

1. Accepts client_id and client_secret via form data
2. Validates the credentials against our client database
3. Issues JWT tokens with appropriate scopes
4. Handles token validation for protected endpoints

The implementation follows the OAuth 2.0 specification for the client credentials grant type.

## Security Considerations

- In production, replace the hardcoded client credentials with a proper database
- Use HTTPS in production
- Limit CORS origins to trusted domains
- Consider implementing rate limiting
- Rotate client secrets periodically

## Development

For development purposes, the server includes auto-reload functionality. Any changes to the code will automatically restart the server.

## Troubleshooting

If you encounter import errors or other issues:

1. Make sure you've activated the virtual environment
2. Verify that all dependencies are installed: `uv pip list`
3. Check for any error messages in the terminal when starting the server

## License

[MIT License](LICENSE)