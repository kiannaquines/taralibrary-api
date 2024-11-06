import asyncio
from fastapi import WebSocket
from typing import List
import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        logger.debug("Attempting WebSocket connection...")
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug("WebSocket connected.")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.debug("WebSocket disconnected.")

    async def broadcast(self, message: dict):
        """Send a message to all connected WebSocket clients."""
        tasks = []
        message_str = json.dumps(message)  # Convert dict to JSON string
        for connection in self.active_connections:
            tasks.append(connection.send_text(message_str))
        await asyncio.gather(*tasks)


manager = ConnectionManager()

    









