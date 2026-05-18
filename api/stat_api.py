from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from utils.auth import get_current_user_obj
from core.api_exception_handler import handle_api_exception
from core.response_schema import success
from database.models.user import User
from services.stat_service import get_statistics
import json

from database.redis import redis_client

router = APIRouter(tags=["统计数据"])


@router.get("/statistics", summary="获取统计数据")
@handle_api_exception
def get_stat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_obj)
):
    cache_key = f"stat:user:{current_user.id}"
    expire_seconds = 180

    if redis_client:
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return success(data=json.loads(cache_data))

    data = get_statistics(db, current_user)

    if redis_client:
        redis_client.setex(cache_key, expire_seconds, json.dumps(data, ensure_ascii=False))

    return success(data=data)
