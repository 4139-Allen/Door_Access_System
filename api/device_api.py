from fastapi import APIRouter, Depends, Path, Body, Query
from sqlalchemy.orm import Session
from database.db import get_db
from utils.auth import get_current_user_obj, require_admin
from core.api_exception_handler import handle_api_exception
from core.response_schema import success, error
from schemas.device_schema import DeviceCreate, DeviceUpdate, BindUserDevice
from services.device_service import (
    create_device,
    update_device,
    delete_device,
    bind_user_device,
    unbind_user_device,
    get_device_list,
    DEVICE_CACHE_KEY_TEMPLATE,
    CACHE_EXPIRE
)
from database.models.user import User
from database.redis import redis_client
import json
from typing import Optional

router = APIRouter(tags=["【管理员】设备管理"])


# 创建设备
@router.post("/devices", summary="新增设备", description="添加一个新的门禁设备")
@handle_api_exception
def create(
        data: DeviceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    device = create_device(db, data)
    return success(data={"device_id": device.id}, msg="创建设备成功")


# 获取设备列表
@router.get("/devices", summary="获取设备列表")
@handle_api_exception
def get_device_list_endpoint(
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页条数"),
    name: Optional[str] = Query(None, description="设备名称模糊搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_obj)
):
    # 只有无筛选且是第一页时才使用缓存
    use_cache = (name is None and page == 1 and size == 10 and redis_client)

    if use_cache:
        cache_key = DEVICE_CACHE_KEY_TEMPLATE.format(user_id=current_user.id)
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)

    device_data = get_device_list(
        db=db,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin"),
        name=name,
        page=page,
        size=size
    )

    res = success(data={
        "total": device_data["total"],
        "list": device_data["list"]
    })

    # 只有第一页默认配置才缓存
    if use_cache and redis_client:
        cache_key = DEVICE_CACHE_KEY_TEMPLATE.format(user_id=current_user.id)
        redis_client.setex(cache_key, CACHE_EXPIRE, json.dumps(res, ensure_ascii=False))

    return res


# 更新设备
@router.put("/devices/{device_id}", summary="更新设备", description="修改设备名称/状态等信息")
@handle_api_exception
def update(
        device_id: int = Path(...),
        data: DeviceUpdate = Body(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    device = update_device(db, device_id, data)
    if not device:
        return error("设备不存在", code=404)

    return success(msg="更新成功")


# 删除设备
@router.delete("/devices/{device_id}", summary="删除设备")
@handle_api_exception
def delete_device_endpoint(
        device_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    delete_device(db, device_id)
    return success(msg="删除设备成功")


# 绑定设备
@router.post("/devices/{device_id}/bind", summary="绑定用户到设备")
@handle_api_exception
def admin_bind_device(
        device_id: int = Path(..., description="设备ID"),
        data: BindUserDevice = Body(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    bind_user_device(db, data.user_id, device_id, operator_id=current_user.id)
    return success(msg="绑定成功")


# 解绑设备
@router.delete("/devices/{device_id}/unbind", summary="解除用户与设备的绑定")
@handle_api_exception
def unbind_user_device_endpoint(
        device_id: int = Path(..., description="设备ID"),
        user_id: int = Query(..., description="用户ID"),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    unbind_user_device(db, user_id, device_id, operator_id=current_user.id)
    return success(msg="解除绑定成功")
