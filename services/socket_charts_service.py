import asyncio
from fastapi import WebSocket, Depends, WebSocketDisconnect, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Device, Prediction
from services.db_services import get_db
from typing import Dict, List, Any
from datetime import datetime, date, time
from sqlalchemy import func, and_, select


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        tasks = []
        for connection in self.active_connections:
            tasks.append(connection.send_text(message))
        await asyncio.gather(*tasks)


manager = ConnectionManager()

    









