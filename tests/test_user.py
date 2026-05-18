"""
用户服务单元测试
测试登录、注册、删除用户等功能
"""
import pytest
from services.user_service import login_user, db_create_user, delete_user_by_id, change_user_password
from database.models.user import User
from utils.auth import hash_password, verify_password


class TestLoginUser:
    """用户登录测试"""

    def test_login_with_correct_credentials(self, db_session, test_user):
        """测试使用正确的凭据登录"""
        result = login_user(db_session, "testuser", "testpass123")

        assert result.token is not None
        assert result.error is None
        assert result.user.id == test_user.id
        assert result.user.username == "testuser"

    def test_login_with_wrong_password(self, db_session, test_user):
        """测试使用错误的密码登录"""
        result = login_user(db_session, "testuser", "wrongpass")

        assert result.token is None
        assert result.error == "密码错误"
        assert result.user is None

    def test_login_with_nonexistent_user(self, db_session):
        """测试使用不存在的用户名登录"""
        result = login_user(db_session, "nonexistent", "testpass123")

        assert result.token is None
        assert result.error == "用户不存在"
        assert result.user is None


class TestCreateUser:
    """创建用户测试"""

    def test_create_user_success(self, db_session):
        """测试成功创建用户"""
        user = db_create_user(db_session, "newuser", "newpass123", "user")

        assert user.id is not None
        assert user.username == "newuser"
        assert user.role == "user"
        assert verify_password("newpass123", user.password)

    def test_create_admin_user(self, db_session):
        """测试创建管理员用户"""
        user = db_create_user(db_session, "newadmin", "adminpass123", "admin")

        assert user.role == "admin"

    def test_create_duplicate_user(self, db_session, test_user):
        """测试创建重复用户名抛出异常"""
        with pytest.raises(ValueError, match="已存在"):
            db_create_user(db_session, "testuser", "anotherpass", "user")


class TestDeleteUser:
    """删除用户测试"""

    def test_delete_user_success(self, db_session, test_user):
        """测试成功删除用户"""
        result = delete_user_by_id(db_session, test_user.id)

        assert result is True

        # 验证用户已被删除
        deleted_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert deleted_user is None

    def test_delete_nonexistent_user(self, db_session):
        """测试删除不存在的用户抛出异常"""
        with pytest.raises(ValueError, match="用户不存在"):
            delete_user_by_id(db_session, 99999)


class TestChangePassword:
    """修改密码测试"""

    def test_change_password_success(self, db_session, test_user):
        """测试成功修改密码"""
        result = change_user_password(
            db_session,
            test_user,
            "testpass123",
            "newpass456"
        )

        assert result is True
        assert verify_password("newpass456", test_user.password)

    def test_change_password_with_wrong_old_password(self, db_session, test_user):
        """测试使用错误的原密码修改失败"""
        with pytest.raises(ValueError, match="原密码错误"):
            change_user_password(
                db_session,
                test_user,
                "wrongpass",
                "newpass456"
            )

    def test_change_password_too_long(self, db_session, test_user):
        """测试新密码过长抛出异常"""
        long_password = "a" * 100

        with pytest.raises(ValueError, match="新密码过长"):
            change_user_password(
                db_session,
                test_user,
                "testpass123",
                long_password
            )
