from typing import Dict, Set
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.task_channels: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        for task_id, users in list(self.task_channels.items()):
            users.discard(user_id)
            if not users:
                self.task_channels.pop(task_id)

    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")
                self.disconnect(user_id)

    def subscribe_to_task(self, user_id: str, task_id: str):
        if task_id not in self.task_channels:
            self.task_channels[task_id] = set()
        self.task_channels[task_id].add(user_id)

    async def broadcast_task_update(self, task_id: str, message: dict):
        if task_id in self.task_channels:
            for user_id in list(self.task_channels[task_id]):
                await self.send_message(user_id, message)

manager = ConnectionManager()