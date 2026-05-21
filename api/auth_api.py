from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.db import get_db
from schemas.user_schema import UserLogin, UserCreate, PasswordChange
from services.user_service import login_user, change_user_password
from core.api_exception_handler import handle_api_exception
from core.response_schema import ApiResponse, success, error
from utils.auth import logout_token, get_current_user_obj, security
from database.models.user import User

router = APIRouter(tags=["认证管理"])


@router.post("/auth/login", summary="用户登录", response_model=ApiResponse)
@handle_api_exception
def login(data: UserLogin, db: Session = Depends(get_db)):
    result = login_user(db, data.username, data.password)

    if result.error:
        return error(result.error)

    return success({"token": result.token, "role": result.user.role})


@router.post("/auth/register", summary="用户注册", response_model=ApiResponse)
@handle_api_exception
def register_new_user(data: UserCreate, db: Session = Depends(get_db)):
    from services.user_service import db_create_user
    db_create_user(db, data.username, data.password, role="user")
    return success(msg="注册成功")


@router.post("/auth/logout", summary="退出登录", response_model=ApiResponse)
@handle_api_exception
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    logout_token(token)
    return success(msg="退出成功，Token 已失效")


@router.put("/auth/password", summary="修改密码", response_model=ApiResponse)
@handle_api_exception
def change_password(
        data: PasswordChange,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_obj)
):
    change_user_password(db, current_user, data.old_password, data.new_password)
    return success(msg="密码修改成功")
