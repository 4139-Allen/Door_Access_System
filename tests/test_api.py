"""
API 集成测试（接口/测试用例：19/52）
测试 HTTP 接口的完整流程
"""
import pytest

#用户认证（测试用例8）
class TestUserAPI:
    """用户 API 测试"""

    def test_login_success(self, client, test_user):
        """测试登录成功"""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "token" in data["data"]

    def test_login_failure_wrong_password(self, client, test_user):
        """测试登录失败 - 密码错误"""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400
        assert "密码错误" in data.get("msg", "")

    def test_register_new_user(self, client):
        """测试注册新用户"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "newpass123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_register_duplicate_user(self, client, test_user):
        """测试注册重复用户"""
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "password": "anotherpass"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400

    def test_logout_success(self, client, auth_headers):
        """测试退出登录成功"""
        token = auth_headers["Authorization"].split(" ")[1]
        response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_login_with_nonexistent_user(self, client):
        """测试使用不存在的用户名登录"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400
        assert "用户不存在" in data.get("msg", "")

    def test_change_password_success(self, client, db_session, test_user):
        """测试修改密码成功并验证新密码生效"""
        from utils.auth import hash_password, verify_password

        # 1. 确保数据库中用户的初始密码是我们预期的 (testpass123)
        # 注意：conftest 中的 test_user 已经设置了这个密码，这里再次确认或重置以确保环境干净
        test_user.password = hash_password("testpass123")
        db_session.commit()

        # 2. 先登录获取旧 token
        login_res = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert login_res.status_code == 200
        old_token = login_res.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {old_token}"}

        # 3. 发送修改密码请求
        response = client.put("/api/auth/password", json={
            "old_password": "testpass123",
            "new_password": "NewSecurePass456!"
        }, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "密码修改成功"

        # 4. 验证旧密码失效
        old_login_res = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert old_login_res.json()["code"] == 400  # 密码错误

        # 5. 验证新密码生效
        new_login_res = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "NewSecurePass456!"
        })
        assert new_login_res.status_code == 200
        assert new_login_res.json()["code"] == 200
        assert "token" in new_login_res.json()["data"]

    def test_change_password_wrong_old_password(self, client, auth_headers):
        """测试修改密码时原密码错误"""
        response = client.put("/api/auth/password", json={
            "old_password": "wrongpass",
            "new_password": "newpass456"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400

#用户管理（测试用例6）
class TestUserManagementAPI:
    """用户管理 API 测试（管理员）"""

    def test_list_users_as_admin(self, client, admin_headers):
        """测试管理员获取用户列表"""
        response = client.get("/api/users?page=1&size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]

    def test_list_users_as_user_forbidden(self, client, auth_headers):
        """测试普通用户获取用户列表被拒绝"""
        response = client.get("/api/users?page=1&size=10", headers=auth_headers)
        assert response.status_code == 403

    def test_create_user_as_admin(self, client, admin_headers):
        """测试管理员创建用户"""
        response = client.post("/api/users", json={
            "username": "newadminuser",
            "password": "adminpass123"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_create_user_as_user_forbidden(self, client, auth_headers):
        """测试普通用户创建用户被拒绝"""
        response = client.post("/api/users", json={
            "username": "normaluser",
            "password": "userpass123"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_delete_user_as_admin(self, client, admin_headers, db_session):
        """测试管理员删除用户"""
        # 先创建一个临时用户
        from database.models.user import User
        from utils.auth import hash_password
        temp_user = User(username="tempuser", password=hash_password("temppass"), role="user")
        db_session.add(temp_user)
        db_session.commit()

        response = client.delete(f"/api/users/{temp_user.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_user_devices_as_admin(self, client, admin_headers, test_user, test_device, db_session):
        """测试管理员查询用户设备"""
        from database.models.user_device import UserDevice
        binding = UserDevice(user_id=test_user.id, device_id=test_device.id)
        db_session.add(binding)
        db_session.commit()

        response = client.get(f"/api/users/{test_user.id}/devices", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

#设备管理（测试用例8）
class TestDeviceAPI:
    """设备 API 测试"""

    def test_list_devices_requires_auth(self, client):
        """测试列出设备需要认证"""
        response = client.get("/api/devices")

        assert response.status_code == 401

    def test_list_devices_with_auth(self, client, auth_headers):
        """测试认证后列出设备"""
        response = client.get("/api/devices", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_create_device_as_admin(self, client, admin_headers):
        """测试管理员创建设备"""
        response = client.post("/api/devices", json={
            "name": "002",
            "location": "教学楼"
        }, headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_create_device_as_user_forbidden(self, client, auth_headers):
        """测试普通用户创建设备被拒绝"""
        response = client.post("/api/devices", json={
            "name": "003",
            "location": "图书馆"
        }, headers=auth_headers)

        assert response.status_code == 403

    def test_update_device_as_admin(self, client, admin_headers, test_device):
        """测试管理员更新设备"""
        response = client.put(f"/api/devices/{test_device.id}", json={
            "name": "001-updated",
            "status": "offline"
        }, headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_delete_device_as_admin(self, client, admin_headers):
        """测试管理员删除设备"""
        # 先创建设备
        create_response = client.post("/api/devices", json={
            "name": "999",
            "location": "测试位置"
        }, headers=admin_headers)
        device_id = create_response.json()["data"]["device_id"]

        # 删除设备
        response = client.delete(f"/api/devices/{device_id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_bind_user_device_as_admin(self, client, admin_headers, test_user, test_device):
        """测试管理员绑定用户和设备"""
        response = client.post(f"/api/devices/{test_device.id}/bind", json={
            "user_id": test_user.id
        }, headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_unbind_user_device_as_admin(self, client, admin_headers, test_user, test_device, db_session):
        """测试管理员解绑用户和设备"""
        from database.models.user_device import UserDevice

        # 先绑定
        binding = UserDevice(user_id=test_user.id, device_id=test_device.id)
        db_session.add(binding)
        db_session.commit()

        # 再解绑
        response = client.delete(f"/api/devices/{test_device.id}/unbind?user_id={test_user.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

#门禁管理（测试用例3）
class TestDoorAPI:
    """门禁 API 测试"""

    def test_open_door_without_auth(self, client, test_device):
        """测试未认证时开门被拒绝"""
        response = client.post(f"/api/doors/{test_device.id}/open")

        assert response.status_code == 401

    def test_open_door_with_permission(self, client, auth_headers, test_user, test_device, db_session):
        """测试有权限时开门成功"""
        from database.models.user_device import UserDevice

        # 绑定用户和设备
        binding = UserDevice(user_id=test_user.id, device_id=test_device.id)
        db_session.add(binding)
        db_session.commit()

        response = client.post(
            f"/api/doors/{test_device.id}/open",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_open_door_without_permission(self, client, auth_headers, test_device):
        """测试无权限时开门失败"""
        response = client.post(
            f"/api/doors/{test_device.id}/open",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 403

#日志管理（测试用例3）
class TestLogAPI:
    """日志 API 测试"""

    def test_query_logs_requires_auth(self, client):
        """测试查询日志需要认证"""
        response = client.get("/api/door-logs?page=1&size=10")

        assert response.status_code == 401

    def test_query_logs_as_user(self, client, auth_headers):
        """测试普通用户查询自己的日志"""
        response = client.get(
            "/api/door-logs?page=1&size=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_query_logs_as_admin(self, client, admin_headers):
        """测试管理员查询所有日志"""
        response = client.get(
            "/api/door-logs?page=1&size=10",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

#统计数据（测试用例3）
class TestStatAPI:
    """统计 API 测试"""

    def test_get_statistics_requires_auth(self, client):
        """测试获取统计数据需要认证"""
        response = client.get("/api/statistics")

        assert response.status_code == 401

    def test_get_statistics_as_user(self, client, auth_headers):
        """测试普通用户获取统计数据"""
        response = client.get("/api/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "user_total" in data["data"]
        assert "device_total" in data["data"]
        assert "today_log" in data["data"]

    def test_get_statistics_as_admin(self, client, admin_headers):
        """测试管理员获取统计数据"""
        response = client.get("/api/statistics", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 管理员应该能看到更大的数值
        assert data["data"]["user_total"] >= 1
        assert data["data"]["device_total"] >= 0
        assert data["data"]["today_log"] >= 0

#AI API（5）
class TestAIAPI:
    """AI API 测试"""

    def test_ai_chat_requires_auth(self, client):
        """测试 AI 聊天需要认证"""
        response = client.post("/api/ai/chat", json={
            "message": "打开大门"
        })
        assert response.status_code == 401

    def test_ai_chat_as_user_forbidden(self, client, auth_headers):
        """测试普通用户不能使用 AI 功能"""
        response = client.post("/api/ai/chat", json={
            "message": "打开大门"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 应该返回提示仅管理员可用
        assert "reply" in data["data"]
        assert "仅管理员" in data["data"]["reply"] or "权限" in data["data"]["reply"]

    def test_ai_chat_as_admin(self, client, admin_headers):
        """测试管理员可以使用 AI 功能"""
        response = client.post("/api/ai/chat", json={
            "message": "打开大门"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "reply" in data["data"]

    def test_ai_chat_empty_message(self, client, admin_headers):
        """测试 AI 聊天空消息"""
        response = client.post("/api/ai/chat", json={
            "message": ""
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # 应该能处理空消息
        assert data["code"] in [200, 400]

    def test_ai_chat_missing_message_field(self, client, admin_headers):
        """测试 AI 聊天缺少 message 字段"""
        response = client.post("/api/ai/chat", json={}, headers=admin_headers)
        # Pydantic 验证会返回 422
        assert response.status_code in [200, 422]


#边界情况（16）
class TestEdgeCases:
    """边界情况和异常测试"""

    def test_update_nonexistent_device(self, client, admin_headers):
        """测试更新不存在的设备"""
        response = client.put("/api/devices/99999", json={
            "name": "nonexistent"
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_delete_nonexistent_device(self, client, admin_headers):
        """测试删除不存在的设备"""
        response = client.delete("/api/devices/99999", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_open_nonexistent_door(self, client, auth_headers):
        """测试打开不存在的门"""
        response = client.post("/api/doors/99999/open", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_bind_nonexistent_device(self, client, admin_headers, test_user):
        """测试绑定不存在的设备"""
        response = client.post(f"/api/devices/99999/bind", json={
            "user_id": test_user.id
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_delete_nonexistent_user(self, client, admin_headers):
        """测试删除不存在的用户"""
        response = client.delete("/api/users/99999", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_get_nonexistent_user_devices(self, client, admin_headers):
        """测试查询不存在用户的设备"""
        response = client.get("/api/users/99999/devices", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # 应该返回空列表或错误
        assert data["code"] in [200, 404]

    def test_list_users_with_pagination(self, client, admin_headers):
        """测试用户列表分页"""
        response = client.get("/api/users?page=1&size=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
        # 验证返回的是列表且数量不超过5
        assert isinstance(data["data"]["list"], list)
        assert len(data["data"]["list"]) <= 5

    def test_list_users_with_username_filter(self, client, admin_headers, test_user):
        """测试用户列表按用户名筛选"""
        response = client.get(f"/api/users?username={test_user.username}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 应该至少找到一个匹配的用户
        assert data["data"]["total"] >= 1

    def test_list_users_with_role_filter(self, client, admin_headers):
        """测试用户列表按角色筛选"""
        response = client.get("/api/users?role=admin", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 验证返回的都是管理员
        for user in data["data"]["list"]:
            assert user["role"] == "admin"

    def test_create_duplicate_device(self, client, admin_headers, test_device):
        """测试创建重复设备"""
        response = client.post("/api/devices", json={
            "name": test_device.name,
            "location": test_device.location
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400

    def test_bind_duplicate_user_device(self, client, admin_headers, test_user, test_device, db_session):
        """测试重复绑定用户和设备"""
        from database.models.user_device import UserDevice

        # 先绑定
        binding = UserDevice(user_id=test_user.id, device_id=test_device.id)
        db_session.add(binding)
        db_session.commit()

        # 再次绑定应该失败
        response = client.post(f"/api/devices/{test_device.id}/bind", json={
            "user_id": test_user.id
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400

    def test_unbind_nonexistent_binding(self, client, admin_headers, test_user, test_device):
        """测试解绑不存在的绑定关系"""
        response = client.delete(f"/api/devices/{test_device.id}/unbind?user_id={test_user.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # 可能返回成功（幂等）或错误
        assert data["code"] in [200, 400]

    def test_device_list_with_name_filter(self, client, admin_headers, test_device):
        """测试设备列表按名称筛选"""
        response = client.get(f"/api/devices?name={test_device.name}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 应该至少找到一个匹配的设备
        assert len(data["data"]["list"]) >= 1

    def test_change_password_too_short(self, client, auth_headers):
        """测试修改密码时新密码过短"""
        response = client.put("/api/auth/password", json={
            "old_password": "testpass123",
            "new_password": "123"  # 太短
        }, headers=auth_headers)
        # Pydantic 验证失败会返回 422，响应格式是 FastAPI 默认的 detail 结构
        assert response.status_code == 422
        data = response.json()
        # 验证错误通常包含 detail 字段
        assert "detail" in data

    def test_register_with_short_password(self, client):
        """测试注册时密码过短"""
        response = client.post("/api/auth/register", json={
            "username": "shortpassuser",
            "password": "123"  # 太短
        })
        # Pydantic 验证会返回 422
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


    def test_health_check_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


