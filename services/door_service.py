from database.models.device import Device
from database.models.user import User
from database.models.door_log import DoorLog
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from services.device_service import check_user_permission
from utils.service_exception import service_exception_handler
from schemas.door_schema import LogQuery
from utils.logger import AppLogger
from core.exceptions import NotFoundError

logger = AppLogger.get_logger()


def _add_door_log(db: Session, user_id: int, device_id: int, status: str):
    """快速创建开门日志并提交"""
    db.add(DoorLog(
        user_id=user_id,
        device_id=device_id,
        action="开门",
        status=status,
        time=datetime.now()
    ))
    db.commit()


# ==========================================
# 1. 开门核心逻辑
# ==========================================
@service_exception_handler
def open_door_service(db: Session, user_id: int, device_id: int, user_role: str) -> tuple[bool, str]:
    """
    开门核心逻辑，返回 (success: bool, message: str)
    可被 API 和 AI Agent 复用
    """
    # 1. 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("用户不存在")  # 404

    # 2. 查询设备
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        logger.warning(f"🚫 开门失败 | 设备ID: {device_id} | 原因: 设备不存在")
        raise NotFoundError("设备不存在")

    username = user.username
    device_name = device.name

    # 3. 设备状态检查
    if device.status != "online":
        _add_door_log(db, user_id, device_id, "失败：设备不在线")

        logger.warning(f"🚫 开门失败 | 设备: {device_name} | 用户: {username} | 原因: 设备不在线")
        raise PermissionError(f"设备「{device_name}」不在线，无法开门")  # 403

    # 4. 权限判断
    if user_role != "admin":
        if not check_user_permission(db, user_id, device_id):
            _add_door_log(db, user_id, device_id, "失败：无权限，未绑定该设备")

            logger.warning(f"🚫 开门失败 | 设备: {device_name} | 用户: {username} | 原因: 无权限")
            raise PermissionError("无权限操作：你未绑定该设备，无法开门")  # 403

    # 4. 开门成功
    _add_door_log(db, user_id, device_id, "成功")

    logger.info(f"🚪 开门成功 | 设备: {device_name} | 用户: {username} | 用户ID: {user_id}")
    return True, "开门成功"



# =================== 3. 日志查询功能======================
@service_exception_handler
def query_logs(
        db: Session,
        params: LogQuery,
        current_user_id: int,
        is_admin: bool
) -> tuple[int, list]:
    """
    查询门禁日志

    参数:
        db: 数据库会话
        params: LogQuery schema 对象
        current_user_id: 当前用户ID
        is_admin: 是否为管理员

    返回:
        (total, result): 总数和日志列表
    """
    # 基础查询 - 关联设备表获取设备信息
    query = db.query(
        DoorLog,
        Device.name.label("device_name"),
        Device.location.label("device_location"),
        User.username.label("username")
    ).outerjoin(Device, DoorLog.device_id == Device.id
    ).outerjoin(User, DoorLog.user_id == User.id)

    # 权限过滤：非管理员只能查看自己的日志
    if not is_admin:
        query = query.filter(DoorLog.user_id == current_user_id)

    # 构造查询条件
    conditions = []

    # 用户ID筛选（仅管理员可用）
    if params.user_id and is_admin:
        conditions.append(DoorLog.user_id == params.user_id)

    # 设备名称模糊搜索
    if params.device_name:
        conditions.append(Device.name.contains(params.device_name))

    # 状态筛选
    if params.status:
        conditions.append(DoorLog.status == params.status)

    # 时间范围筛选
    if params.start_time:
        conditions.append(DoorLog.time >= params.start_time)
    if params.end_time:
        conditions.append(DoorLog.time <= params.end_time)

    if conditions:
        query = query.filter(and_(*conditions))

    # 按时间倒序排列（最新的在前）
    query = query.order_by(DoorLog.time.desc())

    # 总数
    total = query.count()

    # 分页
    offset = (params.page - 1) * params.size
    logs = query.offset(offset).limit(params.size).all()

    # 格式化返回
    result = []
    for log, device_name, device_location, username in logs:
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": username or "未知用户",
            "device_id": log.device_id,
            "device_name": device_name or "未知设备",
            "device_location": device_location or "未知位置",
            "action": log.action,
            "status": log.status,
            "time": str(log.time) if log.time else None
        })

    return total, result
