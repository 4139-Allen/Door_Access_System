"""
WebSocket 服务测试
测试连接管理、消息推送、断开连接等功能
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from services.websocket_service import ConnectionManager, manager


class TestConnectionManager:
    """连接管理器单元测试"""

    def test_manager_initialization(self):
        """测试管理器初始化"""
        mgr = ConnectionManager()

        assert len(mgr.active_connections) == 0
        assert isinstance(mgr.active_connections, list)

    @pytest.mark.asyncio
    async def test_connect_adds_connection(self):
        """测试连接添加到列表"""
        from unittest.mock import AsyncMock

        mgr = ConnectionManager()
        mock_websocket = AsyncMock()

        await mgr.connect(mock_websocket)

        assert len(mgr.active_connections) == 1
        assert mock_websocket in mgr.active_connections
        mock_websocket.accept.assert_called_once()

    def test_disconnect_removes_connection(self):
        """测试断开连接从列表移除"""
        from unittest.mock import MagicMock

        mgr = ConnectionManager()
        mock_websocket = MagicMock()

        # 先添加
        mgr.active_connections.append(mock_websocket)
        assert len(mgr.active_connections) == 1

        # 再断开
        mgr.disconnect(mock_websocket)

        assert len(mgr.active_connections) == 0
        assert mock_websocket not in mgr.active_connections

    def test_disconnect_nonexistent_connection(self):
        """测试断开不存在的连接不报错"""
        from unittest.mock import MagicMock

        mgr = ConnectionManager()
        mock_websocket = MagicMock()

        # 断开未连接的 websocket 不应该报错
        mgr.disconnect(mock_websocket)

        assert len(mgr.active_connections) == 0

    @pytest.mark.asyncio
    async def test_send_to_admin_single_connection(self):
        """测试向单个管理员推送消息"""
        from unittest.mock import AsyncMock

        mgr = ConnectionManager()
        mock_websocket = AsyncMock()
        mgr.active_connections.append(mock_websocket)

        await mgr.send_to_admin("张三", "001", "校门")

        # 验证发送了 JSON 消息
        mock_websocket.send_json.assert_called_once()
        sent_data = mock_websocket.send_json.call_args[0][0]

        assert sent_data["type"] == "door_open"
        assert sent_data["admin_only"] is True
        assert "张三" in sent_data["message"]
        assert "001" in sent_data["message"]
        assert "校门" in sent_data["message"]

    @pytest.mark.asyncio
    async def test_send_to_admin_multiple_connections(self):
        """测试向多个管理员推送消息"""
        from unittest.mock import AsyncMock

        mgr = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws3 = AsyncMock()

        mgr.active_connections = [mock_ws1, mock_ws2, mock_ws3]

        await mgr.send_to_admin("李四", "002", "教学楼")

        # 所有连接都应该收到消息
        assert mock_ws1.send_json.call_count == 1
        assert mock_ws2.send_json.call_count == 1
        assert mock_ws3.send_json.call_count == 1

    @pytest.mark.asyncio
    async def test_send_to_admin_with_failed_connection(self):
        """测试推送时某个连接失败不影响其他连接"""
        from unittest.mock import AsyncMock

        mgr = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock(side_effect=Exception("Connection lost"))
        mock_ws3 = AsyncMock()

        mgr.active_connections = [mock_ws1, mock_ws2, mock_ws3]

        # 不应该抛出异常
        await mgr.send_to_admin("王五", "003", "图书馆")

        # 正常的连接应该收到消息
        assert mock_ws1.send_json.call_count == 1
        assert mock_ws3.send_json.call_count == 1
        # 失败的连接尝试发送但抛出异常（被捕获）
        assert mock_ws2.send_json.call_count == 1

    @pytest.mark.asyncio
    async def test_send_to_admin_no_connections(self):
        """测试没有连接时推送不报错"""
        mgr = ConnectionManager()

        # 不应该抛出异常
        await mgr.send_to_admin("赵六", "004", "食堂")

        assert len(mgr.active_connections) == 0


class TestWebSocketEndpoint:
    """WebSocket 端点集成测试"""

    def test_websocket_connect_and_disconnect(self, client):
        """测试 WebSocket 连接和断开"""
        with client.websocket_connect("/api/ws") as websocket:
            # 连接成功
            assert websocket is not None

            # 发送消息
            websocket.send_text("test message")

            # 断开连接（退出 with 块自动断开）

        # 验证连接已关闭
        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_receive_message(self, client):
        """测试 WebSocket 接收消息"""
        with client.websocket_connect("/api/ws") as websocket:
            # 发送文本消息
            websocket.send_text("Hello WebSocket")

            # 注意：当前实现只接收不响应，所以不需要 receive

        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_multiple_messages(self, client):
        """测试 WebSocket 接收多条消息"""
        messages = ["msg1", "msg2", "msg3"]

        with client.websocket_connect("/api/ws") as websocket:
            for msg in messages:
                websocket.send_text(msg)

        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_json_message(self, client):
        """测试 WebSocket 接收 JSON 消息"""
        import json

        data = {"action": "open_door", "device_id": 1}

        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text(json.dumps(data))

        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_empty_message(self, client):
        """测试 WebSocket 接收空消息"""
        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text("")

        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_special_characters(self, client):
        """测试 WebSocket 接收特殊字符"""
        special_msg = "测试消息 !@#$%^&*()_+-=[]{}|;:',.<>?/~`"

        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text(special_msg)

        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_long_message(self, client):
        """测试 WebSocket 接收长消息"""
        long_msg = "a" * 10000  # 10KB 消息

        with client.websocket_connect("/api/ws") as websocket:
            websocket.send_text(long_msg)

        assert websocket.client_state.name == "DISCONNECTED"

    def test_websocket_rapid_messages(self, client):
        """测试 WebSocket 快速发送多条消息"""
        with client.websocket_connect("/api/ws") as websocket:
            for i in range(100):
                websocket.send_text(f"rapid message {i}")

        assert websocket.client_state.name == "DISCONNECTED"


class TestWebSocketIntegration:
    """WebSocket 与业务逻辑集成测试"""

    @pytest.mark.asyncio
    async def test_manager_send_after_door_open(self):
        """测试开门后推送消息到 WebSocket"""
        from unittest.mock import AsyncMock, patch
        from database.models.user import User
        from database.models.device import Device

        # 模拟用户和设备
        mock_user = User(username="测试用户", role="user")
        mock_device = Device(name="001", location="校门")

        # 模拟 manager
        mgr = ConnectionManager()
        mock_ws = AsyncMock()
        mgr.active_connections.append(mock_ws)

        # 模拟推送
        await mgr.send_to_admin(
            mock_user.username,
            mock_device.name,
            mock_device.location
        )

        # 验证推送内容
        mock_ws.send_json.assert_called_once()
        sent_data = mock_ws.send_json.call_args[0][0]

        assert sent_data["type"] == "door_open"
        assert "测试用户" in sent_data["message"]
        assert "001" in sent_data["message"]
        assert "校门" in sent_data["message"]

    def test_global_manager_instance(self):
        """测试全局 manager 实例存在"""
        from services.websocket_service import manager

        assert manager is not None
        assert isinstance(manager, ConnectionManager)
        assert hasattr(manager, 'active_connections')
        assert hasattr(manager, 'connect')
        assert hasattr(manager, 'disconnect')
        assert hasattr(manager, 'send_to_admin')
