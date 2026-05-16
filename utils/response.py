from pydantic import BaseModel
from typing import Any, Optional
from functools import wraps
from utils.logger import AppLogger

logger = AppLogger.get_logger()


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


def handle_api_exception(func):
    """
    API 层统一异常处理装饰器

    自动捕获常见异常并返回统一格式的错误响应

    使用示例:
        @router.post("/users")
        @handle_api_exception
        def create_user(data: UserCreate, db: Session = Depends(get_db)):
            db_create_user(db, data.username, data.password)
            return success(msg="创建成功")
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"业务逻辑错误 [{func.__name__}]: {str(e)}")
            return error(str(e), code=400)
        except PermissionError as e:
            logger.warning(f"权限错误 [{func.__name__}]: {str(e)}")
            return error(str(e), code=403)
        except FileNotFoundError as e:
            logger.warning(f"资源不存在 [{func.__name__}]: {str(e)}")
            return error(str(e), code=404)
        except TimeoutError as e:
            logger.error(f"请求超时 [{func.__name__}]: {str(e)}")
            return error("请求超时，请稍后重试", code=504)
        except Exception as e:
            logger.error(f"服务器内部错误 [{func.__name__}]: {str(e)}", exc_info=True)
            return error("服务器内部错误，请联系管理员", code=500)

    return wrapper
