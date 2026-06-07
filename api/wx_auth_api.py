from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import httpx

from database.db import get_db
from database.models.user import User
from core.config import WX_APPID, WX_SECRET
from core.api_exception_handler import handle_api_exception
from core.response_schema import ApiResponse, success, error
from utils.auth import create_access_token, verify_password, hash_password, get_current_user
from utils.logger import AppLogger

logger = AppLogger.get_logger()

router = APIRouter(tags=["微信小程序认证"])


class WxLoginRequest(BaseModel):
    code: str = Field(..., description="wx.login() 获取的临时登录凭证")


class WxBindRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")


def code2session(code: str) -> dict:
    """用 code 换取 openid 和 session_key"""
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WX_APPID,
        "secret": WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    with httpx.Client(timeout=10) as client:
        resp = client.get(url, params=params)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        logger.warning(f"⚠️  微信 code2session 失败 | errcode: {data.get('errcode')} | errmsg: {data.get('errmsg')}")
        raise ValueError(f"微信登录失败：{data.get('errmsg', 'code 无效')}")

    return data


def get_or_create_user_by_openid(db: Session, openid: str) -> User:
    """根据 openid 查找或创建用户"""
    user = db.query(User).filter(User.openid == openid).first()

    if user:
        return user

    # 新用户：用 openid 前8位作为用户名，生成随机密码
    base_username = openid[:8]
    username = base_username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    # 生成一个随机密码（用户后续可通过绑定账号来设置密码）
    import secrets
    random_password = secrets.token_urlsafe(16)

    user = User(
        username=username,
        password=hash_password(random_password),
        role="user",
        openid=openid
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"👤 微信小程序新用户注册 | 用户名: {username} | 用户ID: {user.id}")
    return user


@router.post("/auth/wx-login", summary="微信小程序登录", response_model=ApiResponse)
@handle_api_exception
def wx_login(data: WxLoginRequest, db: Session = Depends(get_db)):
    # 1. 校验配置
    if not WX_APPID or not WX_SECRET:
        return error("微信登录未配置，请联系管理员", code=500)

    # 2. code 换 openid
    wechat_data = code2session(data.code)
    openid = wechat_data["openid"]

    # 3. 查找或创建用户
    user = get_or_create_user_by_openid(db, openid)

    # 4. 生成 JWT
    token = create_access_token({"sub": str(user.id)})

    logger.info(f"✅ 微信小程序登录成功 | 用户ID: {user.id} | 用户名: {user.username}")

    return success({
        "token": token,
        "role": user.role,
        "username": user.username,
        "has_password": user.password is not None and len(user.password) > 0
    })


@router.put("/auth/wx-bind", summary="绑定已有账号到微信", response_model=ApiResponse)
@handle_api_exception
def wx_bind(
    data: WxBindRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """将已有账号绑定到当前微信登录的用户"""
    # 查找当前微信用户
    wx_user = db.query(User).filter(User.id == current_user_id).first()
    if not wx_user:
        return error("用户不存在", code=404)

    # 查找要绑定的目标账号
    target_user = db.query(User).filter(User.username == data.username).first()
    if not target_user:
        return error("用户名不存在", code=404)

    if not verify_password(data.password, target_user.password):
        return error("密码错误", code=400)

    # 如果目标账号已绑定其他微信，拒绝
    if target_user.openid and target_user.openid != wx_user.openid:
        return error("该账号已绑定其他微信", code=400)

    # 将微信用户的 openid 转移到目标账号
    target_user.openid = wx_user.openid
    db.delete(wx_user)
    db.commit()

    # 为目标账号生成新 token
    token = create_access_token({"sub": str(target_user.id)})

    logger.info(f"🔗 微信绑定账号成功 | 微信用户ID: {current_user_id} -> 账号: {target_user.username}")

    return success({
        "token": token,
        "role": target_user.role,
        "username": target_user.username
    })
