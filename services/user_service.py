from sqlalchemy.orm import Session

from core.config import AUTO_CREATE_ADMIN, ADMIN_USERNAME, ADMIN_PASSWORD
from core.exceptions import NotFoundError
from utils.service_exception import service_exception_handler
from database.db import SessionLocal
from database.models.user import User
from database.models.door_log import DoorLog
from database.models.user_device import UserDevice
from utils.auth import verify_password, create_access_token, hash_password
from typing import Optional, NamedTuple
from utils.logger import AppLogger
from services.stat_service import invalidate_all_stat_cache

logger = AppLogger.get_logger()


class LoginResult(NamedTuple):
    """登录结果"""
    token: Optional[str]
    error: Optional[str]
    user: Optional[User]


def login_user(db: Session, username: str, password: str) -> LoginResult:
    """
    用户登录

    返回:
        LoginResult: 包含 token、error_message 和 user 的命名元组
    """
    user = db.query(User).filter(User.username == username).first()

    if not user:
        logger.warning(f"❌ 登录失败 | 用户名: {username} | 原因: 用户不存在")
        return LoginResult(None, "用户不存在", None)

    if not verify_password(password, user.password):
        logger.warning(f"❌ 登录失败 | 用户名: {username} | 原因: 密码错误")
        return LoginResult(None, "密码错误", None)

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"✅ 用户登录成功 | 用户名: {username} | 用户ID: {user.id}")

    return LoginResult(token, None, user)


@service_exception_handler
def db_create_user(db: Session, username: str, password: str, role: str = "user") -> User:
    """
    创建新用户

    参数:
        db: 数据库会话
        username: 用户名
        password: 密码
        role: 角色，默认为 user

    返回:
        User: 创建的用户对象

    异常:
        ValueError: 用户名已存在
    """
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.warning(f"⚠️  创建用户失败 | 用户名: {username} | 原因: 已存在")
        raise ValueError(f"用户名 '{username}' 已存在")

    user = User(username=username, password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    invalidate_all_stat_cache()

    logger.info(f"👤 创建用户成功 | 用户名: {username} | 角色: {role} | 用户ID: {user.id}")
    return user

@service_exception_handler
def delete_user_by_id(db: Session, user_id: int) -> bool:
    """
    删除用户及其关联数据

    参数:
        db: 数据库会话
        user_id: 用户ID

    返回:
        bool: 是否删除成功
    """
    # 先检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"⚠️  删除用户失败 | 用户ID: {user_id} | 原因: 用户不存在")
        raise NotFoundError("用户不存在")

    username = user.username

    # 检查用户是否绑定了设备，已绑定则拒绝删除
    has_bind = db.query(UserDevice).filter(UserDevice.user_id == user_id).first()
    if has_bind:
        raise ValueError("该用户已绑定设备，请先解绑后再删除")

    # 删除用户（DoorLog 由数据库 ondelete=SET NULL 自动置空 user_id）
    db.delete(user)
    db.commit()

    invalidate_all_stat_cache()

    logger.info(f"🗑️  删除用户成功 | 用户名: {username} | 用户ID: {user_id}")
    return True


def get_users_list(db: Session, page: int, size: int, username: Optional[str] = None, role: Optional[str] = None) -> \
tuple[int, list]:
    """
    获取用户列表（支持分页和筛选）

    参数:
        db: 数据库会话
        page: 页码
        size: 每页数量
        username: 用户名模糊搜索
        role: 角色筛选

    返回:
        (total, users): 总数和用户列表
    """
    query = db.query(User)

    if username:
        query = query.filter(User.username.contains(username))
    if role:
        query = query.filter(User.role == role)

    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()

    return total, users


def get_user_devices(db: Session, user_id: int) -> list:
    """
    获取用户绑定的设备ID列表

    参数:
        db: 数据库会话
        user_id: 用户ID

    返回:
        list: 设备ID列表
    """
    binds = db.query(UserDevice).filter(UserDevice.user_id == user_id).all()
    return [b.device_id for b in binds]


@service_exception_handler
def change_user_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
    """
    修改用户密码

    参数:
        db: 数据库会话
        user: 用户对象
        old_password: 原密码
        new_password: 新密码

    返回:
        bool: 是否修改成功

    异常:
        ValueError: 原密码错误或密码长度不符合要求
    """
    if not verify_password(old_password, user.password):
        logger.warning(f"❌ 修改密码失败 | 用户: {user.username} | 原因: 原密码错误")
        raise ValueError("原密码错误")

    if len(new_password) < 6:
        logger.warning(f"❌ 修改密码失败 | 用户: {user.username} | 原因: 密码长度不足6位")
        raise ValueError("密码长度不能小于6位")

    if len(new_password.encode('utf-8')) > 72:
        logger.warning(f"❌ 修改密码失败 | 用户: {user.username} | 原因: 新密码过长")
        raise ValueError("新密码过长，不能超过72字节")

    user.password = hash_password(new_password)
    db.commit()

    logger.info(f"🔑 修改密码成功 | 用户: {user.username} | 用户ID: {user.id}")
    return True


"""
管理员初始化
用于创建默认管理员账户
"""
def init_admin():
    """
    初始化默认管理员账户
    """
    if not AUTO_CREATE_ADMIN:
        logger.info("ℹ️  自动创建管理员功能已禁用")
        return

    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin_exists = db.query(User).filter(User.role == "admin").first()

        if admin_exists:
            logger.info("✅ 管理员账户已存在")
            return

        # 复用 db_create_user 创建管理员
        admin_user = db_create_user(db, ADMIN_USERNAME, ADMIN_PASSWORD, role="admin")

        logger.info("=" * 50)
        logger.info("✅ 默认管理员账户创建成功！")
        logger.info(f"👤 用户名: {admin_user.username}")
        logger.info(f"🔑 密码: {ADMIN_PASSWORD}")
        logger.warning("⚠️  请在首次登录后立即修改密码！")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"❌ 创建管理员失败: {str(e)}")
        raise
    finally:
        db.close()


