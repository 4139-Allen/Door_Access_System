from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.db import get_db
from database.models.user import User
from schemas.user_schema import UserLogin, UserCreate, PasswordChange
from services.user_service import (login_user, db_create_user, delete_user_by_id,
               get_users_list, get_user_devices, change_user_password)
from core.api_exception_handler import handle_api_exception
from core.response_schema import success, error
from utils.auth import logout_token, get_current_user_obj, security, require_admin
from typing import Optional

router = APIRouter(tags=["【管理员】用户管理"])


@router.post("/auth/login", summary="用户登录")
def login(data: UserLogin, db: Session = Depends(get_db)):
    result = login_user(db, data.username, data.password)

    if result.error:
        return error(result.error)

    return success({"token": result.token, "role": result.user.role})


@router.post("/auth/register", summary="用户注册")
@handle_api_exception
def register_new_user(data: UserCreate, db: Session = Depends(get_db)):
    db_create_user(db, data.username, data.password, role="user")
    return success(msg="注册成功")


@router.post("/auth/logout", summary="退出登录")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    logout_token(token)
    return success(msg="退出成功，Token 已失效")


@router.put("/auth/password", summary="修改密码")
@handle_api_exception
def change_password(
        data: PasswordChange,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_obj)
):
    """
    修改当前登录用户的密码

    需要验证原密码，并设置新密码
    """
    change_user_password(db, current_user, data.old_password, data.new_password)
    return success(msg="密码修改成功")

@router.get("/users", summary="获取用户列表")
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


@router.post("/users", summary="创建用户")
@handle_api_exception
def create_new_user(
        data: UserCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    db_create_user(db, data.username, data.password)
    return success(msg="创建成功")


@router.delete("/users/{user_id}", summary="删除用户")
@handle_api_exception
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    delete_user_by_id(db, user_id)
    return success("删除成功")


@router.get("/users/{user_id}/devices", summary="查询用户绑定的设备")
@handle_api_exception
def get_user_devices_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    device_list = get_user_devices(db, user_id)
    return success(data=device_list)

