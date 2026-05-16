# 1. 导入核心包
from fastapi import APIRouter

# 2. 导入子路由
from api.user_api import router as user_router
from api.door_api import router as door_router
from api.device_api import router as device_router
from api.stat_api import router as stat_router
from api.ai_agent import router as ai_router
from api.websocket_api import router as websocket_router

# 3. 创建总路由
routers = APIRouter()

# 4. 注册子路由
routers.include_router(user_router)    # 用户管理
routers.include_router(door_router)    # 门禁管理
routers.include_router(device_router)  # 设备管理
routers.include_router(stat_router)    # 统计数据
routers.include_router(ai_router)      # AI智能助手
routers.include_router(websocket_router)    # WebSocket


