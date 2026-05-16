"""
管理员初始化脚本
用于创建默认管理员账户
"""
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models.user import User
from utils.auth import hash_password
from core.config import ADMIN_USERNAME, ADMIN_PASSWORD, AUTO_CREATE_ADMIN
from utils.logger import AppLogger

logger = AppLogger.get_logger()


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

        # 使用配置中的管理员信息
        admin_username = ADMIN_USERNAME
        admin_password = ADMIN_PASSWORD

        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == admin_username).first()
        if existing_user:
            logger.warning(f"⚠️  用户名 '{admin_username}' 已存在")
            return

        # 哈希密码并创建管理员
        hashed_password = hash_password(admin_password)
        admin_user = User(
            username=admin_username,
            password=hashed_password,
            role="admin"
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info("=" * 50)
        logger.info("✅ 默认管理员账户创建成功！")
        logger.info(f"👤 用户名: {admin_username}")
        logger.info(f"🔑 密码: {admin_password}")
        logger.warning("⚠️  请在首次登录后立即修改密码！")
        logger.info("=" * 50)

    except Exception as e:
        db.rollback()
        logger.error(f"❌ 创建管理员失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
