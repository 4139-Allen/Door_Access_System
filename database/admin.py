"""
管理员初始化脚本
用于创建默认管理员账户
"""
from sqlalchemy.orm import Session
from database.db import SessionLocal, engine, Base
from database.models.user import User
from utils.auth import hash_password
from core.config import ADMIN_USERNAME, ADMIN_PASSWORD, AUTO_CREATE_ADMIN
import sys


def init_admin():
    """
    初始化默认管理员账户
    """
    print("\n[Admin Init] 开始初始化管理员账户...")

    if not AUTO_CREATE_ADMIN:
        print("[Admin Init] ℹ️  自动创建管理员功能已禁用")
        return

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin_exists = db.query(User).filter(User.role == "admin").first()

        if admin_exists:
            print("[Admin Init] ✅ 管理员账户已存在")
            return

        # 使用配置中的管理员信息
        admin_username = ADMIN_USERNAME
        admin_password = ADMIN_PASSWORD

        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == admin_username).first()
        if existing_user:
            print(f"[Admin Init] ⚠️  用户名 '{admin_username}' 已存在")
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

        print("[Admin Init] ✅ 默认管理员账户创建成功！")
        print(f"[Admin Init] 👤 用户名: {admin_username}")
        print(f"[Admin Init] 🔑 密码: {admin_password}")
        print("[Admin Init] ⚠️  请在首次登录后立即修改密码！")

    except Exception as e:
        db.rollback()
        print(f"[Admin Init] ❌ 创建管理员失败: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
