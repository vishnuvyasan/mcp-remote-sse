from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn
import asyncio
import logging
from typing import List

from app.auth.oauth import get_current_client
from app.auth.routes import router as auth_router
from app.calculator.calculator import Calculator
from app.sse.sse_manager import SSEManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Machine Communication Protocol server with calculator tools and SSE communication",
    version="1.0.0"
)

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include authentication router
app.include_router(auth_router)

# Initialize components
calculator = Calculator()
sse_manager = SSEManager()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "MCP Server is running"}

# Calculator endpoints
@app.post("/calculator/add", dependencies=[Depends(get_current_client)])
async def add(a: float, b: float):
    result = calculator.add(a, b)
    return {"operation": "add", "result": result}

@app.post("/calculator/subtract", dependencies=[Depends(get_current_client)])
async def subtract(a: float, b: float):
    result = calculator.subtract(a, b)
    return {"operation": "subtract", "result": result}

@app.post("/calculator/multiply", dependencies=[Depends(get_current_client)])
async def multiply(a: float, b: float):
    result = calculator.multiply(a, b)
    return {"operation": "multiply", "result": result}

@app.post("/calculator/divide", dependencies=[Depends(get_current_client)])
async def divide(a: float, b: float):
    try:
        result = calculator.divide(a, b)
        return {"operation": "divide", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Improved SSE endpoint implementation
@app.get("/events")
async def events(request: Request):
    """
    Server-Sent Events endpoint with improved error handling
    """
    client_id = sse_manager.register_client()
    logger.info(f"Client {client_id} connected to /events")
    
    async def event_generator():
        try:
            while True:
                # Check if client is still connected
                if await request.is_disconnected():
                    logger.info(f"Client {client_id} disconnected")
                    sse_manager.remove_client(client_id)
                    break
                    
                # Check for messages
                if await sse_manager.has_message(client_id):
                    message = await sse_manager.get_message(client_id)
                    yield {"data": message}
                
                # Prevent CPU hogging
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in SSE stream for client {client_id}: {str(e)}")
            sse_manager.remove_client(client_id)
        finally:
            # Ensure client is removed when the connection ends
            sse_manager.remove_client(client_id)
            
    return EventSourceResponse(event_generator())

# Additional SSE endpoint at /events/sse for compatibility
@app.get("/events/sse")
async def events_sse(request: Request):
    """
    Alternative SSE endpoint
    """
    return await events(request)

# Additional SSE endpoint at /calculator/sse for compatibility
@app.get("/calculator/sse")
async def calculator_sse(request: Request):
    """
    Alternative SSE endpoint for calculator
    """
    return await events(request)

# Send message to all SSE clients
@app.post("/broadcast", dependencies=[Depends(get_current_client)])
async def broadcast(message: str):
    """
    Broadcast a message to all connected SSE clients
    """
    await sse_manager.broadcast(message)
    return {"status": "Message broadcast"}

# Add a well-known endpoint for OAuth discovery
@app.get("/.well-known/oauth-authorization-server")
async def oauth_config():
    """
    OAuth 2.0 Authorization Server Metadata
    """
    return {
        "issuer": "http://localhost:8001",
        "token_endpoint": "http://localhost:8001/token",
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "grant_types_supported": ["client_credentials"],
        "scopes_supported": ["calculator", "sse"]
    }

# Add a well-known endpoint for OAuth protected resource discovery
@app.get("/.well-known/oauth-protected-resource")
async def protected_resource_config():
    """
    OAuth 2.0 Protected Resource Metadata
    """
    return {
        "resource_server": "http://localhost:8001",
        "authorization_server": "http://localhost:8001",
        "scopes_supported": ["calculator", "sse"]
    }

# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "connected_clients": len(sse_manager.clients)
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

# Made with Bob
