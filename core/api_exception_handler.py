"""
 API异常
"""
from functools import wraps
from utils.logger import AppLogger
from core.response_schema import error
from core.exceptions import NotFoundError, AuthError

logger = AppLogger.get_logger()


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
        except NotFoundError as e:
            logger.warning(f"资源不存在 [{func.__name__}]: {str(e)}")
            return error(str(e), code=404)
        except AuthError as e:
            logger.warning(f"认证失败 [{func.__name__}]: {str(e)}")
            return error(str(e), code=401)
        except TimeoutError as e:
            logger.error(f"请求超时 [{func.__name__}]: {str(e)}")
            return error("请求超时，请稍后重试", code=504)
        except Exception as e:
            logger.error(f"服务器内部错误 [{func.__name__}]: {str(e)}", exc_info=True)
            return error("服务器内部错误，请联系管理员", code=500)

    return wrapper
