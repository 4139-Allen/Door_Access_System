from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from services.websocket_service import manager
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from database.redis import redis_client
from database.db import SessionLocal
from database.models.user import User

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # 验证 JWT token
    user_id = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # 检查黑名单和 Redis 活跃 token
        if redis_client:
            if redis_client.exists(f"blacklist:{token}"):
                await websocket.close(code=1008, reason="Token revoked")
                return
            if not redis_client.exists(f"token:{token}"):
                await websocket.close(code=1008, reason="Token expired")
                return
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 查询用户角色
    is_admin = False
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        is_admin = user and user.role == "admin"
    finally:
        db.close()

    await manager.connect(websocket, user_id=int(user_id), is_admin=is_admin)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)