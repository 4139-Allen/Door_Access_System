from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.db import get_db
from schemas.user_schema import UserLogin, UserCreate, PasswordChange
from services.user_service import login_user, change_user_password
from core.api_exception_handler import handle_api_exception
from core.response_schema import ApiResponse, success, error
from utils.auth import logout_token, get_current_user_obj, security
from utils.rate_limiter import login_limiter
from database.models.user import User

router = APIRouter(tags=["认证管理"])


@router.post("/auth/login", summary="用户登录", response_model=ApiResponse)
@handle_api_exception
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    # 频率限制：基于客户端 IP，5次/60秒
    client_ip = request.client.host if request.client else "unknown"
    login_limiter.check(client_ip)

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
def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 支持两种 token 传递方式
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    else:
        token = request.headers.get("X-Token")

    if not token:
        return error("未提供认证凭证", code=401)

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
