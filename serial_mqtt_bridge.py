"""
串口转 MQTT 桥接脚本
通过 CH340 连接 STM32，转发开门命令到 MQTT，并将设备状态上报到 MQTT

硬件连接：
  STM32 PA9 (TX)  -> CH340 RXD
  STM32 PA10 (RX) <- CH340 TXD
  GND             <-> GND

用法：
  python serial_mqtt_bridge.py

依赖：
  pip install pyserial paho-mqtt
"""

import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import threading
import time
import sys
from datetime import datetime

# ==================== 配置 ====================
SERIAL_PORT = None          # 自动检测，或手动指定如 'COM3'
SERIAL_BAUD = 9600          # 波特率，与 STM32 一致

MQTT_BROKER_HOST = '127.0.0.1'
MQTT_BROKER_PORT = 1883
MQTT_USERNAME = ''
MQTT_PASSWORD = ''
MQTT_TOPIC_PREFIX = 'door'
DEVICE_ID = '001'           # 设备编号，与 STM32 中的 DEVICE_ID 一致

# ==================== 全局变量 ====================
ser = None
mqtt_client = None
running = True


def find_ch340_port():
    """自动查找 CH340 串口"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'CH340' in port.description or 'CH340' in port.hwid:
            print(f"[串口] 找到 CH340: {port.device} - {port.description}")
            return port.device
    # 如果没找到 CH340，列出所有串口让用户选择
    if ports:
        print("[串口] 未找到 CH340，可用串口:")
        for i, port in enumerate(ports):
            print(f"  {i + 1}. {port.device} - {port.description}")
        try:
            choice = int(input("请选择串口编号: ")) - 1
            if 0 <= choice < len(ports):
                return ports[choice].device
        except (ValueError, IndexError):
            pass
    return None


def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT 连接回调"""
    if rc == 0:
        print(f"[MQTT] 已连接到 {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        # 订阅开门命令
        topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/command"
        client.subscribe(topic, qos=1)
        print(f"[MQTT] 已订阅: {topic}")
        # 发送上线状态
        status_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"
        client.publish(status_topic, "ONLINE", qos=1)
        print(f"[MQTT] 已发送上线状态: {status_topic} -> ONLINE")
    else:
        print(f"[MQTT] 连接失败，返回码: {rc}")


def on_mqtt_disconnect(client, userdata, rc):
    """MQTT 断开回调"""
    if rc != 0:
        print(f"[MQTT] 意外断开 (rc={rc})，将自动重连...")


def on_mqtt_message(client, userdata, msg):
    """MQTT 消息回调 - 收到开门命令"""
    global ser
    try:
        payload = msg.payload.decode().strip()
        print(f"[MQTT] 收到命令 [{msg.topic}]: {payload}")

        if payload == "OPEN_DOOR" and ser and ser.is_open:
            # 转发到 STM32
            ser.write(b"OPEN_DOOR\n")
            print(f"[串口] 已发送: OPEN_DOOR\\n")

            # 等待 STM32 响应
            response = wait_for_response(timeout=3)
            if response:
                print(f"[串口] 收到响应: {response}")
                # 上报开门结果到 MQTT
                status_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"
                client.publish(status_topic, "OK", qos=1)
                print(f"[MQTT] 已上报: {status_topic} -> OK")

                # 记录开门日志（可以通过 MQTT 让后端记录）
                log_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/log"
                log_data = f'{{"action":"远程开门","status":"成功","time":"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"}}'
                client.publish(log_topic, log_data, qos=1)
            else:
                print("[串口] 等待响应超时")
                status_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"
                client.publish(status_topic, "TIMEOUT", qos=1)

    except Exception as e:
        print(f"[错误] 处理 MQTT 消息失败: {e}")


def wait_for_response(timeout=3):
    """等待 STM32 响应"""
    global ser
    start_time = time.time()
    buffer = b""
    while time.time() - start_time < timeout:
        if ser and ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            buffer += data
            if b"\n" in buffer:
                return buffer.decode().strip()
        time.sleep(0.05)
    return None


def serial_reader():
    """串口读取线程 - 接收 STM32 上报的状态"""
    global ser, mqtt_client, running
    buffer = ""
    while running:
        try:
            if ser and ser.is_open and ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        print(f"[串口] 收到: {line}")
                        # 处理 STM32 上报的状态
                        handle_stm32_message(line)
            else:
                time.sleep(0.05)
        except Exception as e:
            if running:
                print(f"[错误] 串口读取失败: {e}")
            time.sleep(1)


def handle_stm32_message(message):
    """处理 STM32 上报的消息"""
    global mqtt_client
    if not mqtt_client:
        return

    status_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"

    # 映射 STM32 消息到 MQTT 状态
    status_map = {
        "OK": "OK",                    # 远程开门成功
        "PWD_OK": "PWD_OK",           # 密码开门成功
        "FP_OK": "FP_OK",             # 指纹开门成功
        "CARD_OK": "CARD_OK",         # 刷卡开门成功
        "ONLINE": "ONLINE",           # 设备上线
    }

    status = status_map.get(message, message)
    mqtt_client.publish(status_topic, status, qos=1)
    print(f"[MQTT] 已上报: {status_topic} -> {status}")


def send_heartbeat():
    """心跳线程 - 定期发送设备在线状态"""
    global mqtt_client, running
    while running:
        try:
            if mqtt_client and mqtt_client.is_connected():
                status_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"
                mqtt_client.publish(status_topic, "ONLINE", qos=1)
            time.sleep(30)  # 每 30 秒发送一次心跳
        except Exception as e:
            print(f"[错误] 心跳发送失败: {e}")
            time.sleep(5)


def main():
    global ser, mqtt_client, running

    print("=" * 60)
    print("STM32 串口转 MQTT 桥接工具")
    print("=" * 60)
    print(f"设备编号: {DEVICE_ID}")
    print(f"MQTT Broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    print()

    # 1. 查找串口
    port = SERIAL_PORT or find_ch340_port()
    if not port:
        print("[错误] 未找到可用串口，请检查 CH340 连接")
        sys.exit(1)

    # 2. 打开串口
    try:
        ser = serial.Serial(port, SERIAL_BAUD, timeout=0.1)
        print(f"[串口] 已打开 {port}，波特率 {SERIAL_BAUD}")
        # 清空缓冲区
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    except Exception as e:
        print(f"[错误] 打开串口失败: {e}")
        sys.exit(1)

    # 3. 连接 MQTT
    try:
        mqtt_client = mqtt.Client(client_id=f"serial-bridge-{DEVICE_ID}", clean_session=True)
        if MQTT_USERNAME:
            mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_disconnect = on_mqtt_disconnect
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.reconnect_delay_set(min_delay=1, max_delay=30)

        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        mqtt_client.loop_start()
        print(f"[MQTT] 正在连接 {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
    except Exception as e:
        print(f"[错误] MQTT 连接失败: {e}")
        print("[提示] 请确保 MQTT Broker 已启动 (docker-compose up -d mosquitto)")
        ser.close()
        sys.exit(1)

    # 4. 启动串口读取线程
    reader_thread = threading.Thread(target=serial_reader, daemon=True)
    reader_thread.start()

    # 5. 启动心跳线程
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

    print()
    print("=" * 60)
    print("桥接已启动！等待命令...")
    print("开门命令: 在 MQTT 客户端发送 OPEN_DOOR 到 door/001/command")
    print("按 Ctrl+C 退出")
    print("=" * 60)
    print()

    # 6. 主循环 - 也可以从命令行手动发送命令
    try:
        while running:
            try:
                user_input = input()
                if user_input.strip().upper() == "OPEN_DOOR":
                    ser.write(b"OPEN_DOOR\n")
                    print("[串口] 已手动发送: OPEN_DOOR")
                elif user_input.strip().upper() == "QUIT":
                    break
                elif user_input.strip():
                    ser.write((user_input.strip() + "\n").encode())
                    print(f"[串口] 已发送: {user_input.strip()}")
            except EOFError:
                break
    except KeyboardInterrupt:
        pass

    # 7. 清理
    print("\n[退出] 正在关闭...")
    running = False
    if mqtt_client:
        # 发送离线状态
        status_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/status"
        mqtt_client.publish(status_topic, "OFFLINE", qos=1)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    if ser:
        ser.close()
    print("[退出] 已关闭")


if __name__ == "__main__":
    main()
