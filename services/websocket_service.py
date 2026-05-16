from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    # 【管理员专用推送】
    async def send_to_admin(self, username: str, device_name: str, location: str):
        msg = {
            "type": "door_open",
            "admin_only": True,
            "message": f"【{username}】打开了【{device_name}】({location})"
        }
        for conn in self.active_connections:
            try:
                await conn.send_json(msg)
            except:
                continue

manager = ConnectionManager()