from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from utils.auth import get_current_user_obj
from core.api_exception_handler import handle_api_exception
from core.response_schema import ApiResponse, success
from database.models.user import User
from services.stat_service import get_statistics
from database.redis import cache_get_json, cache_set_json

router = APIRouter(tags=["统计数据"])


@router.get("/statistics", summary="获取统计数据", response_model=ApiResponse)
@handle_api_exception
def get_stat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_obj)
):
    cache_key = f"stat:user:{current_user.id}"
    expire_seconds = 180

    cached = cache_get_json(cache_key)
    if cached:
        return success(data=cached)

    data = get_statistics(db, current_user)

    cache_set_json(cache_key, data, expire_seconds)

    return success(data=data)
