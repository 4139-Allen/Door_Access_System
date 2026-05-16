
from pydantic import BaseModel, Field, field_validator
import re

# 前端登录时 → 必须按这个格式传参
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")


# 前端注册时 → 必须按这个格式传参
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能少于6个字符')
        if len(v) > 72:
            raise ValueError('密码长度不能超过72个字符')
        return v

# 修改密码请求模型
class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=72, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=72, description="新密码")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度不能少于6个字符')
        if len(v) > 72:
            raise ValueError('新密码长度不能超过72个字符')
        return v

