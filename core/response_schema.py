"""
统一响应返回
"""
from pydantic import BaseModel
from typing import Any, Optional

# 统一返回模型 → 让接口文档正常显示
class ApiResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None


def success(data=None, msg="操作成功"):
    """
    成功响应

    参数:
        data: 响应数据
        msg: 成功消息

    返回:
        dict: 统一格式的响应
    """
    return {
        "code": 200,
        "msg": msg,
        "data": data
    }


def error(msg="操作失败", code=400):
    """
    错误响应

    参数:
        msg: 错误消息
        code: 错误码

    返回:
        dict: 统一格式的响应
    """
    return {
        "code": code,
        "msg": msg,
        "data": None
    }
