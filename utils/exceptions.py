"""
通用异常处理装饰器和工具函数
用于统一 Service 层的异常处理和日志记录
"""
import functools
import logging
from typing import Callable, Any
from sqlalchemy.orm import Session

# 配置日志
logger = logging.getLogger(__name__)


def service_exception_handler(func: Callable) -> Callable:
    """
    Service 层异常处理装饰器

    自动处理数据库事务回滚和异常日志记录

    使用示例:
        @service_exception_handler
        def create_user(db: Session, data: UserCreate):
            # 业务逻辑
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 从参数中提取 db session
        db = None
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break

        if not db:
            db = kwargs.get('db')

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # 如果有 db session，执行回滚
            if db:
                db.rollback()

            # 记录错误日志
            logger.error(f"Service [{func.__name__}] 执行失败: {str(e)}", exc_info=True)

            # 重新抛出异常，让 API 层决定如何响应
            raise Exception(f"{func.__name__} 执行失败: {str(e)}")

    return wrapper


def handle_query_exception(default_value: Any = None):
    """
    查询类操作的异常处理装饰器

    参数:
        default_value: 发生异常时的默认返回值

    使用示例:
        @handle_query_exception(default_value=[])
        def get_all_users(db: Session):
            return db.query(User).all()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Service [{func.__name__}] 查询失败: {str(e)}")
                return default_value

        return wrapper

    return decorator
