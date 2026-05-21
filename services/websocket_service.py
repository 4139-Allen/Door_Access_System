from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_info: Dict[int, dict] = {}  # id(websocket) -> {user_id, is_admin}

    async def connect(self, websocket: WebSocket, user_id: int, is_admin: bool):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_info[id(websocket)] = {"websocket": websocket, "user_id": user_id, "is_admin": is_admin}

    def disconnect(self, websocket: WebSocket):
        self.user_info.pop(id(websocket), None)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    # 【管理员专用推送】
    async def send_to_admin(self, username: str, device_name: str, location: str):
        msg = {
            "type": "door_open",
            "admin_only": True,
            "message": f"【{username}】打开了【{device_name}】({location})"
        }
        for conn_id, info in self.user_info.items():
            if info["is_admin"]:
                try:
                    await info["websocket"].send_json(msg)
                except:
                    continue

manager = ConnectionManager()