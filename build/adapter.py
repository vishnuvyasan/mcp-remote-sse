
import json
from app.main import app
from fastapi.responses import JSONResponse

async def handle_request(request_data):
    """Handle incoming requests from Cloudflare Workers."""
    try:
        # Parse the request data
        method = request_data.get("method", "GET")
        path = request_data.get("path", "/")
        query_string = request_data.get("query", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", None)
        
        # Create a FastAPI compatible request
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "path": path,
            "query_string": query_string.encode(),
            "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        }
        
        # Process the request through FastAPI
        response = await app(scope, receive=None, send=None)
        
        # Return the response
        return {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": response.body.decode() if hasattr(response, "body") else "",
        }
    except Exception as e:
        # Handle any errors
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
