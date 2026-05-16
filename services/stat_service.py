from sqlalchemy.orm import Session
from database.models.user import User
from database.models.device import Device
from database.models.door_log import DoorLog
from database.models.user_device import UserDevice
from datetime import datetime, date
from utils.exceptions import handle_query_exception
from typing import TypedDict


class StatisticsResult(TypedDict):
    user_total: int
    device_total: int
    today_log: int


def get_today_start() -> datetime:
    """获取今天开始时间"""
    return datetime.combine(date.today(), datetime.min.time())


@handle_query_exception(default_value={"user_total": 0, "device_total": 0, "today_log": 0})
def get_statistics(db: Session, user: User) -> StatisticsResult:
    """获取统计数据"""
    today_start = get_today_start()

    if user.role == "admin":
        user_total = db.query(User).count()
        device_total = db.query(Device).count()
        today_log = db.query(DoorLog).filter(
            DoorLog.time >= today_start
        ).count()
    else:
        user_total = 1
        device_total = db.query(UserDevice).filter(
            UserDevice.user_id == user.id
        ).count()
        today_log = db.query(DoorLog).filter(
            DoorLog.user_id == user.id,
            DoorLog.time >= today_start
        ).count()

    return {
        "user_total": user_total,
        "device_total": device_total,
        "today_log": today_log
    }
