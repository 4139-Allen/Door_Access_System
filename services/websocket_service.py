import asyncio
import json
from typing import List, Dict, Optional, Tuple

from fastapi import WebSocket
from jose import jwt, JWTError

from core.config import SECRET_KEY, ALGORITHM
from database.db import SessionLocal
from database.models.user import User
from database.redis import redis_client
from utils.logger import AppLogger

logger = AppLogger.get_logger()

# 认证超时（秒）
WS_AUTH_TIMEOUT = 10


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_info: Dict[int, dict] = {}  # id(websocket) -> {user_id, is_admin}

    async def connect(self, websocket: WebSocket, user_id: int, is_admin: bool):
        """注册已认证的 WebSocket 连接（accept 已由调用方完成）"""
        self.active_connections.append(websocket)
        self.user_info[id(websocket)] = {"websocket": websocket, "user_id": user_id, "is_admin": is_admin}

    def disconnect(self, websocket: WebSocket):
        self.user_info.pop(id(websocket), None)
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_to_admin(self, username: str, device_name: str, location: str):
        """向所有在线管理员推送开门通知"""
        msg = {
            "type": "door_open",
            "admin_only": True,
            "message": f"【{username}】打开了【{device_name}】({location})"
        }
        for conn_id, info in self.user_info.items():
            if info["is_admin"]:
                try:
                    await info["websocket"].send_json(msg)
                except Exception as e:
                    logger.warning(f"WebSocket 推送失败: {e}")
                    continue


manager = ConnectionManager()


async def authenticate_websocket(websocket: WebSocket) -> Optional[Tuple[int, bool]]:
    """
    WebSocket 认证

    返回: (user_id, is_admin) 或 None（认证失败时已发送错误消息并关闭连接）
    """
    # 等待客户端发送认证消息（带超时）
    raw = await asyncio.wait_for(websocket.receive_text(), timeout=WS_AUTH_TIMEOUT)
    data = json.loads(raw)

    if data.get("type") != "auth":
        await websocket.send_json({"type": "auth", "status": "failed", "msg": "请先发送认证信息"})
        return None

    token = data.get("token", "")
    if not token:
        await websocket.send_json({"type": "auth", "status": "failed", "msg": "Token 不能为空"})
        return None

    # 验证 JWT
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    uid = payload.get("sub")
    if uid is None:
        await websocket.send_json({"type": "auth", "status": "failed", "msg": "Token 无效"})
        return None

    # 检查黑名单和 Redis 活跃 token
    if redis_client:
        if redis_client.exists(f"blacklist:{token}"):
            await websocket.send_json({"type": "auth", "status": "failed", "msg": "Token 已注销"})
            return None
        if not redis_client.exists(f"token:{token}"):
            await websocket.send_json({"type": "auth", "status": "failed", "msg": "Token 已过期"})
            return None

    user_id = int(uid)

    # 查询用户角色
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        is_admin = user and user.role == "admin"
    finally:
        db.close()

    await websocket.send_json({"type": "auth", "status": "ok"})
    logger.info(f"WebSocket 认证成功: user_id={user_id}, is_admin={is_admin}")

    return user_id, is_admin
