import redis
from redis.exceptions import RedisError
from core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
from utils.logger import AppLogger

logger = AppLogger.get_logger()


class RedisCli:
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._initialized:
            cls._initialized = True
            try:
                cls._instance = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                cls._instance.ping()
                logger.info("✅ Redis 连接成功")
            except RedisError as e:
                logger.warning(f"⚠️  Redis 未启动或配置错误: {e}，将继续运行但影响部分功能（如登录状态管理）")
                cls._instance = None
        return cls._instance


redis_client = RedisCli()
