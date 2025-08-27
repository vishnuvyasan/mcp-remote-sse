// worker.js - Cloudflare Worker entry point for FastAPI application

// Import required modules
import { createApp } from 'fastapi-worker';

// Create a FastAPI application instance
const app = createApp();

// Define the fetch handler for the worker
addEventListener('fetch', (event) => {
  event.respondWith(handleRequest(event.request));
});

// Handle incoming requests
async function handleRequest(request) {
  try {
    // Pass the request to the FastAPI application
    const response = await app.handle(request);
    return response;
  } catch (error) {
    // Handle any errors
    console.error('Error handling request:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}

// Define a DurableObject for SSE connections
export class SSEConnection {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.clients = new Map();
  }

  // Handle incoming requests to the DurableObject
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === '/events' || path === '/events/sse' || path === '/calculator/sse') {
      return this.handleSSE(request);
    } else if (path === '/broadcast') {
      return this.handleBroadcast(request);
    } else {
      return new Response('Not Found', { status: 404 });
    }
  }

  // Handle SSE connections
  async handleSSE(request) {
    // Generate a unique client ID
    const clientId = crypto.randomUUID();
    
    // Create a new ReadableStream for SSE
    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();
    
    // Store the client
    this.clients.set(clientId, writer);
    
    // Remove the client when the connection is closed
    request.signal.addEventListener('abort', () => {
      this.clients.delete(clientId);
      console.log(`Client ${clientId} disconnected`);
    });
    
    // Return the SSE response
    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }

  // Handle broadcast requests
  async handleBroadcast(request) {
    // Parse the message from the request
    const url = new URL(request.url);
    const message = url.searchParams.get('message');
    
    if (!message) {
      return new Response('Missing message parameter', { status: 400 });
    }
    
    // Broadcast the message to all clients
    const encoder = new TextEncoder();
    const data = encoder.encode(`data: ${message}\n\n`);
    
    let count = 0;
    for (const writer of this.clients.values()) {
      try {
        await writer.write(data);
        count++;
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
    
    return new Response(JSON.stringify({ status: 'Message broadcast', clients: count }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

// Export the DurableObject
export { SSEConnection as DurableObject };

// Made with Bob
