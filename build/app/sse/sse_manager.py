import asyncio
import uuid
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SSEManager:
    """
    Manager for Server-Sent Events (SSE) connections.
    Handles client registration, message queuing, and broadcasting.
    """
    
    def __init__(self):
        # Dictionary to store message queues for each client
        self.clients: Dict[str, asyncio.Queue] = {}
        logger.info("SSE Manager initialized")
    
    def register_client(self) -> str:
        """
        Register a new client and create a message queue for it.
        
        Returns:
            str: A unique client ID
        """
        client_id = str(uuid.uuid4())
        self.clients[client_id] = asyncio.Queue()
        logger.info(f"Client {client_id} registered")
        return client_id
    
    def remove_client(self, client_id: str) -> None:
        """
        Remove a client and its message queue.
        
        Args:
            client_id: The ID of the client to remove
        """
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client {client_id} removed")
    
    async def send_message(self, client_id: str, message: str) -> bool:
        """
        Send a message to a specific client.
        
        Args:
            client_id: The ID of the client to send the message to
            message: The message to send
            
        Returns:
            bool: True if the message was sent, False otherwise
        """
        if client_id in self.clients:
            await self.clients[client_id].put(message)
            logger.info(f"Message sent to client {client_id}")
            return True
        logger.warning(f"Failed to send message: client {client_id} not found")
        return False
    
    async def broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        for client_id in list(self.clients.keys()):
            await self.send_message(client_id, message)
        logger.info(f"Message broadcast to {len(self.clients)} clients")
    
    async def has_message(self, client_id: str) -> bool:
        """
        Check if a client has any messages in its queue.
        
        Args:
            client_id: The ID of the client to check
            
        Returns:
            bool: True if the client has messages, False otherwise
        """
        return client_id in self.clients and not self.clients[client_id].empty()
    
    async def get_message(self, client_id: str) -> Optional[str]:
        """
        Get the next message for a client.
        
        Args:
            client_id: The ID of the client to get a message for
            
        Returns:
            Optional[str]: The next message, or None if the client doesn't exist
        """
        if client_id in self.clients:
            return await self.clients[client_id].get()
        return None

# Made with Bob
