"""
AI Agent 服务层
适配学校场景:设备编号(001、002...) + 学校位置
要求:必须提供用户指令、设备编号、位置信息三个要素
支持多轮对话上下文记忆(使用 Redis 存储)
"""
import json
import re
import requests
from typing import Optional
from sqlalchemy.orm import Session
from database.models.user import User
from database.models.device import Device
from services.door_service import open_door_service
from core.config import DEEPSEEK_API_KEY, AI_API_URL, AI_MODEL, AI_TIMEOUT, AI_TEMPERATURE
from core.ai_system_prompt import get_ai_system_prompt
from database.redis import redis_client
from utils.logger import AppLogger

logger = AppLogger.get_logger()

# Redis 上下文配置
AI_CONTEXT_PREFIX = "ai:context:user:"
AI_CONTEXT_EXPIRE = 900

# 位置关键词(学校场景)
LOCATION_KEYWORDS = [
    '校门', '正门', '大门', '后门', '东门', '西门', '南门', '北门',
    '教学楼', '实验楼', '图书馆', '宿舍', '男生宿舍', '女生宿舍',
    '行政楼', '办公楼', '食堂', '餐厅', '体育馆', '运动场'
]


def normalize_device_number(device_str: str) -> str:
    """标准化设备编号为三位数字格式"""
    if not device_str:
        return ""

    numbers = re.findall(r'\d+', device_str)
    if not numbers:
        return device_str.strip()

    num = int(numbers[0])
    return f"{num:03d}" if 1 <= num <= 999 else device_str.strip()


def extract_context_from_message(message: str, context: dict) -> dict:
    """从用户消息中提取上下文信息"""
    updated = context.copy()

    # 提取设备编号
    device_number = normalize_device_number(message)
    if device_number and len(device_number) == 3 and device_number.isdigit():
        updated['device_number'] = device_number

    # 提取位置关键词
    for keyword in LOCATION_KEYWORDS:
        if keyword in message:
            updated['location'] = keyword
            break

    # 提取开门意图
    if any(word in message for word in ['打开', '开启', '开门', '开']):
        updated['intent'] = 'open_door'

    return updated


def _redis_operation(operation: str, user_id: int, data=None):
    """通用 Redis 操作封装"""
    if not redis_client:
        return False if operation == 'save' else ({} if operation == 'load' else False)

    key = f"{AI_CONTEXT_PREFIX}{user_id}"

    try:
        if operation == 'save':
            redis_client.setex(key, AI_CONTEXT_EXPIRE, json.dumps(data, ensure_ascii=False))
            return True
        elif operation == 'load':
            data_str = redis_client.get(key)
            return json.loads(data_str) if data_str else {}
        elif operation == 'delete':
            redis_client.delete(key)
            return True
    except Exception as e:
        logger.error(f"Redis {operation} 操作失败: {e}")
        return False if operation != 'load' else {}


def save_context_to_redis(user_id: int, context: dict) -> bool:
    """保存上下文到 Redis"""
    return _redis_operation('save', user_id, context)


def load_context_from_redis(user_id: int) -> dict:
    """从 Redis 加载上下文"""
    return _redis_operation('load', user_id)


def clear_context_from_redis(user_id: int) -> bool:
    """清除用户的上下文"""
    return _redis_operation('delete', user_id)


def build_context_info(context: dict) -> str:
    """构建上下文信息字符串"""
    if not context:
        return ""

    info_parts = []
    if context.get('device_number'):
        info_parts.append(f"设备编号:{context['device_number']}")
    if context.get('location'):
        info_parts.append(f"位置:{context['location']}")
    if context.get('intent'):
        info_parts.append("用户想要开门")

    return ', '.join(info_parts)


def parse_ai_command(message: str, user_id: int, context: dict = None):
    """解析 AI 命令，支持上下文记忆"""
    if not DEEPSEEK_API_KEY:
        return {"type": "text", "msg": "AI 密钥未配置"}

    # 合并上下文信息
    context_info = build_context_info(context)
    enhanced_message = f"{message}\n\n[上下文信息:{context_info}]" if context_info else message

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": get_ai_system_prompt()},
            {"role": "user", "content": enhanced_message}
        ],
        "temperature": AI_TEMPERATURE
    }

    try:
        response = requests.post(AI_API_URL, headers=headers, json=data, timeout=AI_TIMEOUT)
        response.raise_for_status()
        ai_raw = response.json()["choices"][0]["message"]["content"].strip()

        # 尝试解析为 JSON
        try:
            result = json.loads(ai_raw)
            device_name = normalize_device_number(result.get("device_name", "").strip())
            location = result.get("location", "").strip()

            # 校验设备编号格式
            if device_name and len(device_name) == 3 and device_name.isdigit():
                location = location or (context.get('location') if context else "")
                return {"type": "device", "name": device_name, "location": location}
            elif device_name:
                return {"type": "text", "msg": f"请问{device_name}的设备编号是多少?请使用三位数字格式,如001、002等。"}
            elif location:
                return {"type": "text", "msg": f"请问{location}的哪个设备编号需要打开呢?"}
            else:
                return {"type": "text", "msg": "请问你想打开哪个门呢?请告诉我设备编号(如001)和位置。"}

        except json.JSONDecodeError:
            return {"type": "text", "msg": ai_raw}

    except requests.exceptions.Timeout:
        return {"type": "text", "msg": "AI服务超时,请稍后再试"}
    except requests.exceptions.RequestException as e:
        logger.error(f"AI请求失败: {e}")
        return {"type": "text", "msg": "AI服务暂时异常"}
    except Exception as e:
        logger.error(f"AI解析异常: {e}")
        return {"type": "text", "msg": "AI处理失败,请稍后重试"}


def find_device_by_number_and_location(db: Session, device_number: str, location: str) -> Optional[Device]:
    """根据设备编号和位置匹配设备"""
    if not device_number or len(device_number) != 3:
        return None

    # 策略1: 精确匹配设备编号
    device = db.query(Device).filter(Device.name == device_number).first()
    if device:
        return device

    # 策略2: 模糊匹配(兼容不带前导零的情况)
    num = int(device_number)
    patterns = [f"{num:03d}", f"{num:02d}", str(num), f"{num}号", f"第{num}号"]

    for pattern in patterns:
        device = db.query(Device).filter(Device.name.ilike(f"%{pattern}%")).first()
        if device:
            return device

    # 策略3: 仅通过位置匹配(兜底)
    if location:
        devices = db.query(Device).filter(Device.location.ilike(f"%{location}%")).all()
        return devices[0] if devices else None

    return None


def process_ai_chat_command(db: Session, user: User, user_message: str) -> dict:
    """
    处理 AI 聊天命令
    要求三要素: 用户指令、设备编号(001、002...)、位置信息
    """
    if user.role != "admin":
        return {"reply": "仅管理员可使用"}

    # 加载并更新上下文
    context = load_context_from_redis(user.id)
    context = extract_context_from_message(user_message, context)

    # 解析 AI 命令
    ai_result = parse_ai_command(user_message, user.id, context)

    # 处理自然语言回复
    if ai_result["type"] == "text":
        save_context_to_redis(user.id, context)
        return {"reply": ai_result["msg"]}

    # 匹配设备并开门
    device_number = ai_result.get("name")
    location = ai_result.get("location", "")

    device = find_device_by_number_and_location(db, device_number, location)
    if not device:
        reply = f"❌ 未找到设备:{device_number}"
        if location:
            reply += f"(位置:{location})"
        reply += ",请检查设备编号和位置是否正确"
        return {"reply": reply}

    # 执行开门
    success_flag, message = open_door_service(db, user.id, device.id, user.role)

    if success_flag:
        reply = f"✅ 已成功开启:{device.name}"
        if device.location:
            reply += f"({device.location})"
        clear_context_from_redis(user.id)
        return {"reply": reply}
    else:
        return {"reply": f"❌ 开门失败:{message}"}
