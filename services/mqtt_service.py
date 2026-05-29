"""
MQTT 服务层
负责与 MQTT Broker 通信，向硬件设备发布开门命令，订阅设备状态
"""
import asyncio
from typing import Optional
from datetime import datetime

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from core.config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT,
    MQTT_USERNAME, MQTT_PASSWORD, MQTT_TOPIC_PREFIX
)
from database.redis import redis_client
from database.db import SessionLocal
from database.models.device import Device
from database.models.door_log import DoorLog
from services.websocket_service import manager as ws_manager
from utils.service_exception import service_exception_handler
from utils.logger import AppLogger

logger = AppLogger.get_logger()


# ==========================================
# 本地开门日志（密码/指纹/刷卡）
# ==========================================
@service_exception_handler
def _save_local_door_log(db: Session, device_id: str, action: str):
    """记录本地开门日志并推送 WebSocket 通知（由 @service_exception_handler 统一处理异常）"""
    device = db.query(Device).filter(Device.name == device_id).first()
    if not device:
        return
    db.add(DoorLog(
        user_id=None, device_id=device.id,
        action=action, status="成功", time=datetime.now()
    ))
    db.commit()
    logger.info(f"本地开门记录 [{device_id}]: {action}")
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(
                ws_manager.send_to_admin("本地", device.name, device.location or "")
            )
    except RuntimeError:
        pass


class MQTTManager:
    """MQTT 连接管理器，单例模式"""

    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False

    def start(self):
        """初始化并连接 MQTT Broker"""
        try:
            self.client = mqtt.Client(client_id="door-backend", clean_session=True)
            if MQTT_USERNAME:
                self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

            # 启用自动重连（指数退避：1秒 ~ 30秒）
            self.client.reconnect_delay_set(min_delay=1, max_delay=30)

            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
            self.client.loop_start()
            logger.info(f"MQTT 客户端已启动，正在连接 {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        except Exception as e:
            logger.warning(f"MQTT 连接失败，设备控制功能不可用: {e}")
            self.client = None

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            # 订阅所有设备的状态上报
            client.subscribe(f"{MQTT_TOPIC_PREFIX}/+/status", qos=1)
            logger.info(f"MQTT 已连接，已订阅 {MQTT_TOPIC_PREFIX}/+/status")
        else:
            logger.error(f"MQTT 连接失败，返回码: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logger.warning(f"MQTT 意外断开 (rc={rc})，将在后台自动重连...")
        else:
            logger.info("MQTT 正常断开")

    def _on_message(self, client, userdata, msg):
        """处理设备上报的状态消息"""
        parts = msg.topic.split("/")
        if len(parts) != 3 or parts[2] != "status":
            return

        device_id = parts[1]
        payload = msg.payload.decode().strip()
        logger.info(f"MQTT 设备状态上报 [{device_id}]: {payload}")

        # 更新在线状态到 Redis
        if redis_client and payload in ("ONLINE", "OK", "OPENED"):
            redis_client.setex(f"device:online:{device_id}", 70, "online")

        # 记录本地开门日志
        action_map = {"PWD_OK": "密码开门", "FP_OK": "指纹开门", "CARD_OK": "刷卡开门"}
        if payload in action_map:
            db = SessionLocal()
            try:
                _save_local_door_log(db, device_id, action_map[payload])
            finally:
                db.close()

    def publish_command(self, device_name: str, command: str):
        """
        向设备发布命令

        Args:
            device_name: 设备编号（如 "001"）
            command: 命令内容（如 "OPEN_DOOR"）
        """
        if not self.client or not self.connected:
            logger.warning(f"MQTT 未连接，无法发送命令到设备 {device_name}")
            return False

        topic = f"{MQTT_TOPIC_PREFIX}/{device_name}/command"
        result = self.client.publish(topic, command, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"MQTT 命令已发送 [{topic}] -> {command}")
            return True
        else:
            logger.error(f"MQTT 命令发送失败 [{topic}], rc={result.rc}")
            return False

    def stop(self):
        """断开 MQTT 连接"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("MQTT 客户端已关闭")


# 全局单例
mqtt_manager = MQTTManager()
