"""
认证模块单元测试
测试 JWT Token 创建、验证、密码哈希等功能
"""
import pytest
from utils.auth import hash_password, verify_password, create_access_token
from jose import jwt
from core.config import SECRET_KEY, ALGORITHM


class TestPasswordHashing:
    """密码哈希测试"""

    def test_hash_password_creates_hash(self):
        """测试密码能够成功哈希"""
        password = "testpass123"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert isinstance(hashed, str)

    def test_verify_password_correct(self):
        """测试正确密码验证通过"""
        password = "testpass123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """测试错误密码验证失败"""
        hashed = hash_password("correctpass")

        assert verify_password("wrongpass", hashed) is False

    def test_hash_password_too_long(self):
        """测试超长密码抛出异常"""
        long_password = "a" * 100

        with pytest.raises(ValueError, match="密码过长"):
            hash_password(long_password)

    def test_verify_password_too_long(self):
        """测试超长密码验证返回 False"""
        hashed = hash_password("shortpass")
        long_password = "a" * 100

        assert verify_password(long_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """测试相同密码生成不同的哈希值（bcrypt 特性）"""
        password = "testpass123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAccessToken:
    """Token 创建测试"""

    def test_create_access_token(self):
        """测试创建 Token"""
        data = {"sub": "123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_access_token(self):
        """测试解码 Token"""
        data = {"sub": "123"}
        token = create_access_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "123"
        assert "exp" in payload

    def test_token_contains_expiration(self):
        """测试 Token 包含过期时间"""
        data = {"sub": "456"}
        token = create_access_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
