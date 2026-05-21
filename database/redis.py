import json
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


def cache_get_json(key):
    """从 Redis 获取缓存并解析 JSON，无缓存或 Redis 不可用时返回 None"""
    if redis_client:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    return None


def cache_set_json(key, data, expire_seconds):
    """将数据序列化为 JSON 并存入 Redis"""
    if redis_client:
        redis_client.setex(key, expire_seconds, json.dumps(data, ensure_ascii=False))
