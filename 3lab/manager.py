import asyncio
from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[task_id] = websocket

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]

    async def send_message(self, task_id: str, message: dict):
        if task_id in self.active_connections:
            websocket = self.active_connections[task_id]
            await websocket.send_json(message)


manager = WebSocketManager()