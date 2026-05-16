from database.models.device import Device
from database.models.user import User
from database.models.door_log import DoorLog
from database.models.user_device import UserDevice
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from services.device_service import check_user_permission
from utils.exceptions import service_exception_handler
from schemas.door_schema import LogQuery
from utils.logger import AppLogger

logger = AppLogger.get_logger()


# ==========================================
# 1. 开门核心逻辑
# ==========================================
@service_exception_handler
def open_door_service(db: Session, user_id: int, device_id: int, user_role: str) -> tuple[bool, str]:
    """
    开门核心逻辑，返回 (success: bool, message: str)
    可被 API 和 AI Agent 复用
    """
    # 获取用户和设备信息用于日志
    user = db.query(User).filter(User.id == user_id).first()
    device = db.query(Device).filter(Device.id == device_id).first()
    
    username = user.username if user else f"用户ID:{user_id}"
    device_name = device.name if device else f"设备ID:{device_id}"
    
    # 管理员：允许开所有设备
    if user_role != "admin":
        # 普通用户：必须存在绑定关系
        if not check_user_permission(db, user_id, device_id):
            # 写入无权限失败日志
            log = DoorLog(
                user_id=user_id,
                device_id=device_id,
                action="开门",
                status="失败：无权限，未绑定该设备",
                time=datetime.now()
            )
            db.add(log)
            db.commit()
            logger.warning(f"🚫 开门失败 | 设备: {device_name} | 用户: {username} | 原因: 无权限")
            return False, "无权限操作：你未绑定该设备，无法开门"

    # 有权限则正常开门
    log = DoorLog(
        user_id=user_id,
        device_id=device_id,
        action="开门",
        status="成功",
        time=datetime.now()
    )
    db.add(log)
    db.commit()
    logger.info(f"🚪 开门成功 | 设备: {device_name} | 用户: {username} | 用户ID: {user_id}")
    return True, "开门成功"


# ==========================================
# 2. 记录门禁日志
# ==========================================
@service_exception_handler
def create_log(db: Session, user_id: int, device_id: int, action: str, status: str) -> DoorLog:
    """创建门禁日志记录"""
    log = DoorLog(
        user_id=user_id,
        device_id=device_id,
        action=action,
        status=status,
        time=datetime.now()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ==========================================
# 3. 日志查询功能
# ==========================================
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
        Device.location.label("device_location")
    ).outerjoin(Device, DoorLog.device_id == Device.id)

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
    # Deleted:if conditions:
    # Deleted:query = query.filter(and_(*conditions))

    # 按时间倒序排列（最新的在前）
    query = query.order_by(DoorLog.time.desc())

    # 总数
    total = query.count()

    # 分页
    offset = (params.page - 1) * params.size
    logs = query.offset(offset).limit(params.size).all()

    # 格式化返回
    result = []
    for log, device_name, device_location in logs:
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "device_id": log.device_id,
            "device_name": device_name or "未知设备",
            "device_location": device_location or "未知位置",
            "action": log.action,
            "status": log.status,
            "time": str(log.time) if log.time else None
        })

    return total, result
