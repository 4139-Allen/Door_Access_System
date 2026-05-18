"""
开门服务单元测试
测试开门逻辑、权限验证、日志记录等功能
"""
import pytest
from services.door_service import open_door_service, create_log
from database.models.user import User
from database.models.device import Device
from database.models.user_device import UserDevice
from database.models.door_log import DoorLog
from utils.auth import hash_password


class TestOpenDoorService:
    """开门服务测试"""

    def test_admin_can_open_any_door(self, db_session, test_admin, test_device):
        """测试管理员可以打开任意门"""
        success, message = open_door_service(
            db_session,
            test_admin.id,
            test_device.id,
            "admin"
        )

        assert success is True
        assert "开门成功" in message

        # 验证日志已创建
        log = db_session.query(DoorLog).filter(
            DoorLog.user_id == test_admin.id,
            DoorLog.device_id == test_device.id
        ).first()
        assert log is not None
        assert log.status == "成功"

    def test_user_with_permission_can_open_door(self, db_session, test_user, test_device):
        """测试有权限的普通用户可以开门"""
        # 绑定用户和设备
        binding = UserDevice(user_id=test_user.id, device_id=test_device.id)
        db_session.add(binding)
        db_session.commit()

        success, message = open_door_service(
            db_session,
            test_user.id,
            test_device.id,
            "user"
        )

        assert success is True
        assert "开门成功" in message

    def test_user_without_permission_cannot_open_door(self, db_session, test_user, test_device):
        """测试无权限的普通用户不能开门"""
        success, message = open_door_service(
            db_session,
            test_user.id,
            test_device.id,
            "user"
        )

        assert success is False
        assert "无权限" in message

        # 验证失败日志已创建
        log = db_session.query(DoorLog).filter(
            DoorLog.user_id == test_user.id,
            DoorLog.device_id == test_device.id
        ).first()
        assert log is not None
        assert "失败" in log.status
        assert "无权限" in log.status

    def test_open_nonexistent_device(self, db_session, test_user):
        """测试打开不存在的设备"""
        success, message = open_door_service(
            db_session,
            test_user.id,
            99999,
            "user"
        )

        # 应该能处理不存在设备的情况（可能抛出异常或返回失败）
        assert success is False or "失败" in message


class TestCreateLog:
    """创建日志测试"""

    def test_create_log_success(self, db_session, test_user, test_device):
        """测试成功创建日志"""
        log = create_log(
            db_session,
            test_user.id,
            test_device.id,
            "开门",
            "成功"
        )

        assert log.id is not None
        assert log.user_id == test_user.id
        assert log.device_id == test_device.id
        assert log.action == "开门"
        assert log.status == "成功"
        assert log.time is not None

    def test_create_log_with_custom_action(self, db_session, test_user, test_device):
        """测试创建自定义操作日志"""
        log = create_log(
            db_session,
            test_user.id,
            test_device.id,
            "强制开门",
            "警告"
        )

        assert log.action == "强制开门"
        assert log.status == "警告"
