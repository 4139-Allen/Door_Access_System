from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_service import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 只需要等待消息，不需要处理！
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)