from fastapi import WebSocket
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, data: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning("Failed to send to user %s, removing stale connection: %s", user_id, e)
                self.active_connections.pop(user_id, None)

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()
notif_manager = ConnectionManager()
