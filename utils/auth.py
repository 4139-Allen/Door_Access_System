from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# 从统一配置模块导入
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Redis
from database.redis import redis_client
from database.db import get_db
from database.models.user import User

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ====================== 创建 token（存入 Redis）======================
def create_access_token(data: dict) -> str:
    """
    创建 JWT Token 并存储到 Redis

    参数:
        data: 包含用户信息的字典，必须包含 'sub' 字段

    返回:
        str: JWT Token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # 存入 Redis：key=token, value=user_id, 过期时间同步
    if redis_client:
        redis_client.setex(
            f"token:{token}",
            ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            data.get("sub")
        )

    return token


# ====================== 校验用户（先查 Redis + 黑名单）======================
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    验证 Token 并返回用户ID

    参数:
        credentials: HTTP Bearer Token

    返回:
        int: 用户ID

    异常:
        HTTPException: Token 无效或已过期
    """
    token = credentials.credentials

    # ====================== 【加入黑名单校验】======================
    if redis_client and redis_client.exists(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="Token 已注销，请重新登录")

    # 检查 Redis 是否存在（不存在直接判定失效）
    if redis_client and not redis_client.exists(f"token:{token}"):
        raise HTTPException(status_code=401, detail="Token 已退出登录或无效")

    # 正常校验 JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token中未包含用户ID（sub字段缺失）")

        return int(user_id)

    except JWTError:
        if redis_client:
            redis_client.delete(f"token:{token}")
        raise HTTPException(status_code=401, detail="Token无效或已过期")

# ====================== 退出登录（删除缓存 + 加入黑名单）======================
def logout_token(token: str):
    if redis_client:
        # 删除原来的登录缓存
        redis_client.delete(f"token:{token}")
        # 加入黑名单，过期时间和JWT一致（24小时足够）
        redis_client.setex(f"blacklist:{token}", 86400, "true")

# ====================== 获取当前用户对象 ======================
def get_current_user_obj(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """获取当前用户对象，避免在各处重复查询"""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

# ====================== 密码相关======================
def hash_password(password: str) -> str:
    """
    哈希密码

    参数:
        password: 明文密码

    返回:
        str: 哈希后的密码

    异常:
        ValueError: 密码超过72字节
    """
    if len(password.encode('utf-8')) > 72:
        raise ValueError("密码过长")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    验证密码

    参数:
        plain: 明文密码
        hashed: 哈希后的密码

    返回:
        bool: 密码是否匹配
    """
    if len(plain.encode('utf-8')) > 72:
        return False
    return pwd_context.verify(plain, hashed)


# 管理员权限验证
def require_admin(current_user: User = Depends(get_current_user_obj)) -> User:
    """
    管理员权限验证依赖

    使用此依赖的 API 端点将自动验证用户是否为管理员
    如果不是管理员，将返回 403 错误

    使用示例:
        @router.get("/users")
        def list_users(current_user: User = Depends(require_admin)):
            # 只有管理员能访问此接口
            pass

    参数:
        current_user: 当前用户对象（由 get_current_user_obj 提供）

    返回:
        User: 管理员用户对象

    异常:
        HTTPException: 当用户不是管理员时抛出 403 错误
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无管理员权限")
    return current_user

