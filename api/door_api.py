# 标准库
import asyncio

# 第三方库
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

# 项目内部模块
from utils.auth import get_current_user_obj
from database.db import get_db
from services.door_service import open_door_service, query_logs
from utils.response import success, error, handle_api_exception
from database.models.user import User
from database.models.device import Device
from schemas.door_schema import LogQuery
from services.websocket_service import manager

router = APIRouter(tags=["门禁管理"])


@router.post("/doors/{device_id}/open", summary="开启门禁")
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
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            background_tasks.add_task(
                manager.send_to_admin,
                username=current_user.username,
                device_name=device.name,
                location=device.location
            )
        return success(msg=message)

    return error(message)


@router.get("/door-logs", summary="获取开门日志")
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