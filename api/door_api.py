# 标准库

# 第三方库
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

# 项目内部模块
from utils.auth import get_current_user_obj
from database.db import get_db
from services.door_service import open_door_service, query_logs
from core.api_exception_handler import handle_api_exception
from core.response_schema import ApiResponse, success, error
from database.models.user import User
from database.models.device import Device
from schemas.door_schema import LogQuery
from services.websocket_service import manager
from services.mqtt_service import mqtt_manager
from database.redis import redis_client

router = APIRouter(tags=["门禁管理"])


@router.post("/doors/{device_id}/open", summary="开启门禁", response_model=ApiResponse)
@handle_api_exception
def door_open(
    device_id: int,
    background_tasks: BackgroundTasks,  # 这里加上，必须传
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_obj)
):
    # 开门业务逻辑
    success_flag, message = open_door_service(
        db, current_user.id, device_id, current_user.role
    )

    if success_flag:
        # 清除统计数据缓存，确保首页即时刷新
        if redis_client:
            redis_client.delete(f"stat:user:{current_user.id}")

        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            # 发布 MQTT 开门命令给硬件设备
            mqtt_manager.publish_command(device.name, "OPEN_DOOR")

            # WebSocket 通知在线管理员和绑定了该设备的用户
            background_tasks.add_task(
                manager.send_door_event,
                device_id=device.id,
                username=current_user.username,
                device_name=device.name,
                location=device.location,
                action="开门"
            )
        return success(msg=message)


@router.get("/door-logs", summary="获取开门日志", response_model=ApiResponse)
@handle_api_exception
def get_logs(
    params: LogQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_obj)
):
    total, log_list = query_logs(
        db=db,
        params=params,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )

    return success(
        data={"list": log_list, "total": total},
        msg="获取日志成功"
    )