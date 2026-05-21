from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.db import get_db
from database.models.user import User
from schemas.user_schema import UserCreate
from services.user_service import db_create_user, delete_user_by_id, get_users_list, get_user_devices
from core.api_exception_handler import handle_api_exception
from core.response_schema import ApiResponse, success
from utils.auth import get_current_user_obj, require_admin
from typing import Optional

router = APIRouter(tags=["【管理员】用户管理"])


@router.get("/users", summary="获取用户列表", response_model=ApiResponse)
@handle_api_exception
def list_users(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        username: Optional[str] = Query(None, description="用户名模糊搜索"),
        role: Optional[str] = Query(None, description="角色筛选 admin/user"),
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    total, users = get_users_list(db, page, size, username, role)
    return success({
        "list": [{
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
        } for u in users],
        "total": total
    })


@router.post("/users", summary="创建用户", response_model=ApiResponse)
@handle_api_exception
def create_new_user(
        data: UserCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    db_create_user(db, data.username, data.password)
    return success(msg="创建成功")


@router.delete("/users/{user_id}", summary="删除用户", response_model=ApiResponse)
@handle_api_exception
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    delete_user_by_id(db, user_id)
    return success(msg="删除成功")


@router.get("/users/{user_id}/devices", summary="查询用户绑定的设备", response_model=ApiResponse)
@handle_api_exception
def get_user_devices_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    device_list = get_user_devices(db, user_id)
    return success(data=device_list)
