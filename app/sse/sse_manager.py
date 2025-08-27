import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any
from collections import deque

logger = logging.getLogger(__name__)

class SSEManager:
    """
    Server-Sent Events Manager
    Handles client connections and message broadcasting
    """
    
    def __init__(self):
        """Initialize the SSE manager"""
        self.clients: Dict[str, deque] = {}
        self.lock = asyncio.Lock()
        logger.info("SSE Manager initialized")
        
    def register_client(self) -> str:
        """
        Register a new client and return a unique client ID
        """
        client_id = str(uuid.uuid4())
        self.clients[client_id] = deque()
        logger.info(f"Client {client_id} registered")
        return client_id
        
    def remove_client(self, client_id: str) -> None:
        """
        Remove a client from the manager
        """
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client {client_id} removed")
    
    async def has_message(self, client_id: str) -> bool:
        """
        Check if a client has any pending messages
        """
        if client_id not in self.clients:
            return False
        return len(self.clients[client_id]) > 0
    
    async def get_message(self, client_id: str) -> Optional[str]:
        """
        Get the next message for a client
        """
        if client_id not in self.clients or not self.clients[client_id]:
            return None
        
        message = self.clients[client_id].popleft()
        logger.info(f"Message sent to client {client_id}")
        return message
    
    async def send_message(self, client_id: str, message: str) -> bool:
        """
        Send a message to a specific client
        """
        if client_id not in self.clients:
            return False
        
        async with self.lock:
            self.clients[client_id].append(message)
        
        logger.info(f"Message sent to client {client_id}")
        return True
    
    async def broadcast(self, message: str) -> int:
        """
        Broadcast a message to all connected clients
        """
        count = 0
        async with self.lock:
            for client_id, queue in self.clients.items():
                queue.append(message)
                logger.info(f"Message sent to client {client_id}")
                count += 1
        
        logger.info(f"Message broadcast to {count} clients")
        return count

# Made with Bob
