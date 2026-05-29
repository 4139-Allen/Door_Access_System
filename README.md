# 智能门禁管理系统 (Smart Door Access System)

一个基于 FastAPI + Vue 3 + STM32 的全栈智能化门禁管理系统，支持多设备管理、用户权限控制、开门记录查询、AI 智能开门，以及通过 MQTT 实现真实硬件设备通信（密码/指纹/刷卡）。

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg?logo=fastapi)
![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg?logo=vue.js&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-orange.svg?logo=eclipsemosquitto&logoColor=white)
![STM32](https://img.shields.io/badge/STM32-F103-red.svg?logo=stmicroelectronics&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg?logo=docker&logoColor=white)

## 目录

- [系统架构](#系统架构)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [后端说明](#后端说明)
- [前端说明](#前端说明)
- [硬件说明](#硬件说明)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端浏览器                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP / WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                    Nginx (frontend:80)                          │
│    - 静态文件服务 (Vue SPA)                                      │
│    - API 反向代理 (/api/ → fastapi:8000)                        │
│    - WebSocket 代理 (/api/ws → fastapi:8000)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI (fastapi:8000)                       │
│    - RESTful API + WebSocket 服务                                │
│    - MQTT 客户端 → Mosquitto                                    │
│    - AI 助手 (DeepSeek LLM)                                    │
│    - JWT 认证 + RBAC 权限                                       │
└───┬───────────┬───────────┬─────────────────────────────────────┘
    │           │           │
┌───▼───┐   ┌──▼──┐   ┌───▼──────────────────────────────────────┐
│ MySQL │   │Redis│   │          MQTT Broker (Mosquitto)          │
│ :3307 │   │:6379│   │              :1883 (MQTT)                 │
└───────┘   └─────┘   └─────────────────────────┬────────────────┘
                                                 │
                              ┌───────────────────┼───────────────┐
                              │                   │               │
                    ┌─────────▼──────┐  ┌────────▼───────┐  ┌───▼──────────┐
                    │   串口桥接脚本   │  │  ESP32-S3 WiFi │  │  W5500 有线   │
                    │ serial_mqtt    │  │  MQTT 客户端    │  │  MQTT 客户端  │
                    │ bridge (PC)    │  │  (WiFi 网络)    │  │  (以太网)    │
                    └────────┬───────┘  └────────┬───────┘  └───┬──────────┘
                             │ Serial            │ WiFi         │ Ethernet
                    ┌────────▼───────────────────────────────────────────────┐
                    │                    STM32F103 主控                      │
                    │  ┌─────────┐ ┌─────────┐ ┌──────┐ ┌────────┐ ┌─────┐│
                    │  │AS608    │ │RC522    │ │AT24C │ │LCD12864│ │4x4  ││
                    │  │指纹模块 │ │RFID模块 │ │EEPROM│ │显示屏  │ │键盘 ││
                    │  └─────────┘ └─────────┘ └──────┘ └────────┘ └─────┘│
                    │  ┌─────────┐ ┌─────────┐                            │
                    │  │蜂鸣器   │ │电磁锁   │                            │
                    │  └─────────┘ └─────────┘                            │
                    └───────────────────────────────────────────────────────┘
```

### 通信协议分工

| 通道 | 协议 | 用途 |
|------|------|------|
| 浏览器 ↔ Nginx | HTTP / WebSocket | Web 界面访问、实时通知 |
| Nginx ↔ FastAPI | HTTP / WebSocket | API 请求转发 |
| FastAPI ↔ MQTT | MQTT v3.1.1 | 向设备发送开门指令、接收状态上报 |
| STM32 ↔ ESP32-S3 | UART (9600 baud) | 串口通信（WiFi 模式） |
| STM32 ↔ W5500 | 软件 SPI | 以太网通信（有线模式） |
| STM32 ↔ CH340 | Serial (9600 baud) | PC 调试（串口桥接模式） |

**WebSocket 负责：** 前端实时开门通知（管理员接收）
**MQTT 负责：** 硬件设备通信（开门指令下发、设备状态上报、心跳检测、本地开门记录）

---

## 功能特性

### 核心功能
- **用户认证**：JWT Token 认证，支持登录/注册/退出/修改密码，Redis 令牌管理
- **角色权限**：管理员和普通用户两级权限控制（RBAC）
- **设备管理**：设备增删改查、用户绑定/解绑、Redis 缓存加速
- **门禁控制**：远程开门、权限验证、日志自动记录
- **数据统计**：用户数、设备数、今日开门次数统计（Redis 缓存 180s）
- **开门日志**：多维度查询（时间/状态/设备/用户），分页展示，时间倒序

### MQTT 设备通信
- **MQTT Broker**：集成 Eclipse Mosquitto，端口 1883
- **设备控制**：通过 MQTT 向硬件设备发送 `OPEN_DOOR` 指令
- **状态上报**：设备实时上报在线状态（`ONLINE`）、开门记录（`PWD_OK`/`FP_OK`/`CARD_OK`）
- **心跳检测**：设备 30s 上线心跳，70s Redis TTL 超时标记离线
- **本地开门记录**：密码/指纹/刷卡等本地开门方式自动记录到数据库

### 硬件集成（STM32F103）
- **主控芯片**：STM32F103C8T6 (ARM Cortex-M3, 72MHz)
- **指纹识别**：AS608 光学指纹模块（UART, 57600 baud）
- **RFID 刷卡**：MFRC522 非接触式读卡器（软件 SPI, ISO 14443A）
- **密码存储**：AT24C02 EEPROM（软件 I2C, 256 字节）
- **密码键盘**：4x4 矩阵键盘（16 键，GPIO 扫描）
- **显示屏**：LCD12864 液晶显示（3 线串口，128x64 像素）
- **网络连接**：ESP32-S3 WiFi 或 W5500 以太网（编译时切换）
- **执行机构**：电磁锁继电器（500ms 脉冲）+ 蜂鸣器反馈

### 高级功能
- **AI 智能助手**：自然语言控制开门（DeepSeek AI 集成）
  - 支持学校场景：设备编号（001、002...）+ 位置识别
  - 多轮对话上下文记忆（Redis 存储，15 分钟过期）
  - 数据查询：今日开门记录、设备列表、设备状态等
- **WebSocket**：实时门禁状态推送（管理员接收通知）
- **Redis 缓存**：设备列表（60s）、统计数据（180s）、AI 上下文（900s）、设备在线状态（70s）
- **自动初始化**：启动时自动创建数据库、表结构和默认管理员
- **串口桥接**：开发调试用，CH340 USB 转串口 ↔ MQTT 桥接脚本

### 前端界面
- **仪表盘**：欢迎横幅、实时时钟、统计数据卡片、快捷操作、最近开门记录
- **用户管理**：用户列表、搜索筛选、创建/删除用户、查看绑定设备、设备绑定/解绑
- **设备管理**：设备列表、搜索筛选、新增/编辑/删除设备、在线状态切换
- **门禁控制**：设备下拉选择、设备信息卡片、快速开门、个人/全部开门记录
- **开门日志**：日志查询、多维度筛选（用户/设备/状态/时间范围）、分页
- **AI 助手**：悬浮按钮、对话式开门和数据查询、快捷提示、打字动画

---

## 技术栈

### 后端
| 分类 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Web 框架 | FastAPI | 0.104.1 | API 服务 |
| ASGI 服务器 | Uvicorn | 0.24.0 | 异步服务器 |
| 数据库 | MySQL 8.0 + SQLAlchemy | 2.0.23 | ORM 数据访问 |
| 数据库驱动 | PyMySQL | 1.1.0 | MySQL 连接 |
| 缓存 | Redis | 5.0.1 | 缓存 + 令牌管理 |
| 认证 | python-jose + bcrypt | 3.3.0 / 4.0.1 | JWT + 密码哈希 |
| MQTT | paho-mqtt | 1.6.1 | 硬件设备通信 |
| WebSocket | websockets | >=10.0 | 实时通知 |
| 数据验证 | Pydantic | 2.5.0 | 请求/响应校验 |
| AI 接口 | requests | 2.31.0 | DeepSeek API 调用 |
| 测试 | pytest + httpx | 7.4.3 / 0.25.2 | 单元测试 |

### 前端
| 分类 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | Vue 3 | 3.5.32 | UI 框架 |
| 构建工具 | Vite | 8.0.10 | 开发/构建 |
| UI 组件库 | Element Plus | 2.14.0 | UI 组件 |
| 图标 | @element-plus/icons-vue | 2.3.2 | 图标集 |
| 路由 | Vue Router | 4.6.4 | 前端路由 |
| HTTP | Axios | 1.16.0 | API 请求 |

### 硬件
| 分类 | 技术 | 用途 |
|------|------|------|
| 主控 | STM32F103C8T6 (ARM Cortex-M3) | 核心控制 |
| 开发环境 | Keil MDK-ARM V5 | 固件编译 |
| WiFi 模块 | ESP32-S3 (Arduino + PlatformIO) | MQTT WiFi 客户端 |
| 以太网模块 | W5500 (TCP/IP 硬件协议栈) | MQTT 有线客户端 |
| 指纹模块 | AS608 (UART, 57600 baud) | 指纹识别 |
| RFID 模块 | MFRC522 (ISO 14443A) | 刷卡识别 |
| 存储模块 | AT24C02 EEPROM (256B) | 密码/卡号持久化 |
| 显示模块 | LCD12864 (ST7920, 128x64) | 菜单界面 |
| 键盘 | 4x4 矩阵键盘 (16 键) | 密码/菜单输入 |

### 测试
- pytest 7.4.3 + pytest-asyncio 0.21.1 + pytest-cov 4.1.0 + httpx 0.25.2

---

## 快速开始

### 方式一：Docker 部署（推荐）

#### 1. 克隆项目
```bash
git clone <repository-url>
cd door_access_system
```

#### 2. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，**Docker 环境下数据库、Redis 和 MQTT 的主机名必须使用服务名**：
```env
# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=123456
AUTO_CREATE_ADMIN=true

# 数据库配置（Docker 环境必须使用服务名 "mysql"）
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DB=door_access_system

# Redis 配置（Docker 环境必须使用服务名 "redis"）
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# MQTT 配置（Docker 环境必须使用服务名 "mosquitto"）
MQTT_BROKER_HOST=mosquitto
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_TOPIC_PREFIX=door

# CORS 配置
ALLOWED_ORIGINS=*

# AI 配置（可选，未配置不影响系统启动）
DEEPSEEK_API_KEY=your-deepseek-api-key
AI_API_URL=https://api.deepseek.com/v1/chat/completions
AI_MODEL=deepseek-v4-flash
AI_TIMEOUT=15
AI_TEMPERATURE=0.1
```

#### 3. 启动服务
```bash
docker-compose up -d
```

首次启动会自动创建 MySQL 数据库和表结构、默认管理员账户（admin/123456），并启动所有 5 个服务。

#### 4. 访问系统

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost | Nginx 托管的 Vue 应用 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| 健康检查 | http://localhost:8000/health | 服务健康状态 |
| MySQL | localhost:3307 | 外部访问端口 |
| Redis | localhost:6379 | 缓存服务 |
| MQTT | localhost:1883 | MQTT Broker |

**默认管理员**：用户名 `admin`，密码 `123456`（首次登录后请立即修改）

#### 5. 常用操作
```bash
docker-compose ps                          # 查看服务状态
docker-compose logs -f                      # 查看所有日志
docker-compose logs -f fastapi              # 查看后端日志
docker-compose up -d --build fastapi        # 重建后端（代码修改后）
docker-compose up -d --build frontend       # 重建前端
docker-compose down                         # 停止所有服务
docker-compose down -v                      # 停止并删除数据（清空数据库）
```

### 方式二：手动部署（开发模式）

#### 后端
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
# 配置 .env 文件（MYSQL_HOST=localhost, REDIS_HOST=127.0.0.1, MQTT_BROKER_HOST=127.0.0.1）

redis-server                              # 启动 Redis
mosquitto -v                              # 启动 MQTT Broker
python main.py                            # 启动后端（http://127.0.0.1:8000/docs）
```

#### 前端
```bash
cd frontend
npm install
npm run dev                               # 开发服务器 http://localhost:5173
```

#### 串口桥接（连接 STM32 硬件）
```bash
pip install pyserial
python serial_mqtt_bridge.py              # 自动检测 CH340 串口
```

---

## 后端说明

### 项目结构

```
door_access_system/
├── main.py                    # 应用入口（lifespan、CORS、中间件）
├── api/                       # API 层（路由定义）
│   ├── routers.py             # 路由聚合器
│   ├── auth_api.py            # 认证接口（登录/注册/退出/改密）
│   ├── admin_user_api.py      # 用户管理（管理员）
│   ├── device_api.py          # 设备管理
│   ├── door_api.py            # 门禁控制 + 开门日志
│   ├── stat_api.py            # 数据统计
│   ├── ai_agent.py            # AI 助手接口
│   └── websocket_api.py       # WebSocket 实时通知
├── services/                  # 服务层（业务逻辑）
│   ├── user_service.py        # 用户业务
│   ├── device_service.py      # 设备业务（含 Redis 缓存）
│   ├── door_service.py        # 门禁业务 + 日志查询
│   ├── mqtt_service.py        # MQTT 通信管理
│   ├── websocket_service.py   # WebSocket 连接管理 + 认证
│   ├── stat_service.py        # 统计业务
│   └── ai_agent_service.py    # AI 助手业务（DeepSeek）
├── database/                  # 数据层
│   ├── db.py                  # SQLAlchemy 引擎 + 初始化
│   ├── redis.py               # Redis 连接管理（单例 + 自动重连）
│   └── models/                # ORM 模型
│       ├── user.py            # 用户表
│       ├── device.py          # 设备表
│       ├── door_log.py        # 开门日志表
│       └── user_device.py     # 用户-设备绑定表
├── core/                      # 核心配置
│   ├── config.py              # 环境变量加载
│   ├── exceptions.py          # 自定义异常
│   ├── response_schema.py     # 统一响应格式
│   ├── api_exception_handler.py  # 异常处理装饰器
│   └── ai_system_prompt.py    # AI 系统提示词
├── utils/                     # 工具层
│   ├── auth.py                # JWT 认证 + 密码哈希
│   ├── logger.py              # 日志管理（30天轮转）
│   ├── rate_limiter.py        # 请求频率限制
│   └── service_exception.py   # 服务层异常装饰器
├── schemas/                   # Pydantic 校验
│   ├── user_schema.py
│   ├── device_schema.py
│   └── door_schema.py
├── tests/                     # 测试
├── frontend/                  # Vue 3 前端
├── stm32/                     # STM32 硬件固件
├── serial_mqtt_bridge.py      # 串口转 MQTT 桥接脚本
├── docker-compose.yml         # Docker 部署配置
└── requirements.txt           # Python 依赖
```

### 三层架构

```
API 层 (api/)          接收请求、参数校验、调用服务层、返回统一响应
    ↓
服务层 (services/)     业务逻辑、数据库查询、MQTT 通信、缓存管理
    ↓
数据层 (database/)     SQLAlchemy ORM、Redis 缓存、数据库初始化
```

**关键设计模式：**
- **装饰器统一异常处理**：`@handle_api_exception`（HTTP）和 `@handle_websocket_exception`（WebSocket）自动捕获异常并返回标准格式
- **服务层异常装饰器**：`@service_exception_handler` 自动回滚数据库事务
- **单例模式**：Redis 客户端、MQTT 管理器、WebSocket 连接管理器、日志器均为单例
- **Redis 优雅降级**：Redis 不可用时系统正常运行，仅缓存和令牌管理受影响
- **FastAPI 依赖注入**：`get_db`（数据库会话）、`get_current_user_obj`（当前用户）、`require_admin`（管理员校验）

### 数据库模型

**user（用户表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| username | String(50) UNIQUE | 用户名（支持中文） |
| password | String(100) | bcrypt 哈希密码 |
| role | String(20) | 角色：admin / user |
| created_at | DateTime | 创建时间 |

**device（设备表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| name | String(100) | 设备编号（如 "001"） |
| status | String(20) | 状态：online / offline |
| location | String(200) | 位置描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**user_device（用户设备关联表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| user_id | Integer FK → user.id | CASCADE 删除 |
| device_id | Integer FK → device.id | CASCADE 删除 |

**door_log（开门日志表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| user_id | Integer FK → user.id | SET NULL 删除 |
| device_id | Integer FK → device.id | SET NULL 删除 |
| action | String(50) | 动作：开门/密码开门/指纹开门/刷卡开门 |
| status | String(50) | 结果：成功/失败：xxx |
| time | DateTime | 时间 |

索引：`(user_id, time)` 复合索引、`device_id` 索引、`time` 索引

### Redis 缓存策略

| 缓存键 | 过期时间 | 用途 |
|--------|----------|------|
| `token:{token}` | 同 Token 有效期 | 活跃会话令牌 |
| `blacklist:{token}` | 86400s (24h) | 注销令牌黑名单 |
| `cache:device:list:user:{id}` | 60s | 用户设备列表 |
| `stat:user:{id}` | 180s | 统计数据 |
| `ai:context:user:{id}` | 900s (15min) | AI 对话上下文 |
| `device:online:{id}` | 70s | 设备在线状态（MQTT 心跳） |

### MQTT 通信

**主题规范：**
| 主题 | 方向 | 说明 |
|------|------|------|
| `door/{device_id}/command` | 服务器 → 设备 | 开门指令 |
| `door/{device_id}/status` | 设备 → 服务器 | 状态上报 |

**状态上报格式：**
| 消息 | 含义 |
|------|------|
| `ONLINE` | 设备上线 |
| `OK` / `OPENED` | 远程开门成功 |
| `PWD_OK` | 密码开门成功 |
| `FP_OK` | 指纹开门成功 |
| `CARD_OK` | 刷卡开门成功 |

**后端处理流程：**
1. 接收 `ONLINE` → 更新 Redis 设备在线状态（70s TTL）+ 同步数据库
2. 接收 `PWD_OK`/`FP_OK`/`CARD_OK` → 写入 DoorLog（user_id=None）+ WebSocket 通知管理员
3. 发送 `OPEN_DOOR` → QoS 1 发布到设备命令主题

### 异常处理

API 层和 WebSocket 层各有统一的异常处理装饰器，自动捕获：

| 异常类型 | HTTP 状态码 | 说明 |
|----------|------------|------|
| `ValueError` | 400 | 业务逻辑错误 |
| `PermissionError` | 403 | 权限不足 |
| `NotFoundError` | 404 | 资源不存在 |
| `AuthError` | 401 | 认证失败 |
| `TooManyRequestsError` | 429 | 请求频率过高 |
| `TimeoutError` | 504 | 请求超时 |
| `Exception` | 500 | 服务器内部错误 |

---

## 前端说明

### 项目结构

```
frontend/
├── index.html                 # HTML 入口
├── package.json               # 依赖配置
├── vite.config.js             # Vite 构建配置
├── nginx.conf                 # Nginx 配置（SPA + 反向代理）
├── .env                       # 开发环境变量（VITE_API_BASE_URL）
├── .env.production            # 生产环境变量（空，使用相对路径）
└── src/
    ├── main.js                # 入口（注册 Element Plus 中文版）
    ├── App.vue                # 根组件（初始化 WebSocket）
    ├── style.css              # 全局样式
    ├── router/
    │   └── index.js           # 路由配置 + 导航守卫
    ├── views/
    │   ├── Login.vue          # 登录/注册页
    │   ├── Layout.vue         # 主布局（侧边栏 + 头部）
    │   ├── Dashboard.vue      # 仪表盘
    │   ├── Users.vue          # 用户管理（管理员）
    │   ├── Device.vue         # 设备管理（管理员）
    │   ├── Door.vue           # 门禁控制
    │   ├── Log.vue            # 开门日志（管理员）
    │   └── NotFound.vue       # 404 页面
    ├── components/
    │   ├── Layout/
    │   │   ├── SidebarMenu.vue        # 侧边导航菜单
    │   │   └── ChangePasswordModal.vue # 修改密码弹窗
    │   ├── Dashboard/
    │   │   ├── StatCard.vue           # 统计卡片
    │   │   └── AiChatBox.vue          # AI 聊天弹窗
    │   ├── User/
    │   │   ├── UserTable.vue          # 用户表格
    │   │   └── UserBindForm.vue       # 绑定/解绑表单
    │   ├── Device/
    │   │   └── DeviceTable.vue        # 设备表格
    │   ├── Door/
    │   │   └── DoorDeviceSelect.vue   # 设备选择 + 开门按钮
    │   └── common/
    │       ├── BaseTable.vue          # 通用表格 + 分页
    │       ├── SearchFilter.vue       # 通用搜索（防抖 300ms）
    │       ├── AddForm.vue            # 通用新增表单
    │       ├── LogFilter.vue          # 日志筛选（时间/状态/设备）
    │       └── LogTable.vue           # 日志表格
    ├── composables/
    │   └── useListFetch.js    # 分页数据获取 Composable
    ├── utils/
    │   ├── request.js         # Axios 封装（拦截器 + 错误处理）
    │   └── websocket.js       # WebSocket 客户端（自动重连）
    └── styles/
        └── page.css           # 页面共享样式
```

### 路由结构

| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录/注册 | 公开 |
| `/admin/dashboard` | 仪表盘 | 已认证 |
| `/admin/door` | 门禁控制 | 已认证 |
| `/admin/user` | 用户管理 | 管理员 |
| `/admin/device` | 设备管理 | 管理员 |
| `/admin/log` | 开门日志 | 管理员 |
| `/*` | 404 页面 | - |

**导航守卫：** 未登录自动跳转 `/login`；管理员页面角色不匹配自动跳转仪表盘；已登录访问 `/login` 自动跳转仪表盘

### 页面功能

**登录/注册页 (Login.vue)**
- Tab 切换登录和注册
- 表单验证（用户名 1-50 字符，密码 6-72 字符）
- 密码显示/隐藏切换

**仪表盘 (Dashboard.vue)**
- 动态问候语（根据时间：早上好/下午好/晚上好/夜深了）
- 实时时钟（每秒更新）
- 统计卡片：用户总数（管理员）、设备总数、今日开门记录
- 快捷操作按钮
- 最近 5 条开门记录表格
- AI 悬浮按钮

**用户管理 (Users.vue) - 管理员**
- 用户列表（分页、搜索筛选）
- 新增用户
- 用户-设备绑定/解绑
- 查看用户绑定设备
- 删除用户（需先解绑）

**设备管理 (Device.vue) - 管理员**
- 设备列表（分页、搜索、在线状态标识）
- 新增设备（编号 + 位置）
- 编辑设备（名称/位置/状态切换）
- 删除设备（需先解绑）

**门禁控制 (Door.vue)**
- 设备下拉选择（显示在线状态、位置）
- 设备信息卡片（在线时绿色发光效果）
- 开门按钮（离线设备禁用）
- 开门记录表格（管理员看全部，普通用户看自己的）

**开门日志 (Log.vue) - 管理员**
- 完整筛选（用户 ID、设备名、状态、时间范围）
- 分页表格（支持 10/20/50/100 条/页）

### 前端架构特点

- **无状态管理库**：不使用 Pinia/Vuex，通过 `localStorage` 管理 token 和 role
- **Composable 模式**：`useListFetch` 封装分页数据获取（AbortController 防竞态）
- **组件化设计**：视图页处理逻辑和数据获取，展示组件通过 props 接收数据、emit 事件
- **WebSocket 全局初始化**：在 `App.vue` 启动时建立连接，整个会话生命周期保持
- **自动重连**：WebSocket 断开后最多重试 10 次（2 秒间隔），认证失败停止重试
- **Axios 拦截器**：自动附加 Authorization 头、401 自动跳转登录、统一错误提示
- **Nginx 反向代理**：生产环境通过 Nginx 统一入口，静态文件 + API 代理 + WebSocket 代理

---

## 硬件说明

### STM32 主控概述

基于 **STM32F103C8T6**（ARM Cortex-M3, 72MHz）的智能电子密码锁，支持四种开门方式：

1. **密码开门** — 4x4 矩阵键盘输入 6 位数字密码
2. **指纹开门** — AS608 光学指纹传感器
3. **刷卡开门** — MFRC522 RFID 读卡器
4. **远程开门** — MQTT 网络指令

LCD12864 显示屏提供菜单式管理界面，可完成密码修改、指纹录入/删除、卡片注册/删除等操作。

### 硬件模块详情

#### 1. AS608 指纹模块

| 项目 | 说明 |
|------|------|
| 芯片 | AS608 光学指纹传感器 |
| 通信 | UART (USART2, PA2-TX / PA3-RX, 57600 baud) |
| 检测引脚 | PA0（输入下拉，检测手指按压） |
| 数据包格式 | Header(0xEF01) + 4字节地址 + 包标识 + 长度 + 命令 + 数据 + 校验和 |

**主要功能：**
- `PS_GetImage()` — 采集指纹图像
- `PS_GenChar(BufferID)` — 生成特征文件
- `PS_HighSpeedSearch()` — 1:N 高速搜索（页范围 0-20，匹配分数 >50）
- `PS_StoreChar(BufferID, PageID)` — 存储模板到 Flash
- `PS_DeletChar(PageID, N)` — 删除指纹模板
- `PS_ReadSysPara()` — 读取系统参数（最大模板数、安全等级等）

**默认地址：** `0xFFFFFFFF`（广播地址）

#### 2. AT24C02 EEPROM 存储模块

| 项目 | 说明 |
|------|------|
| 芯片 | AT24C02（256 字节 EEPROM） |
| 通信 | 软件 I2C（PB6-SCL, PB7-SDA, ~100kHz） |
| 设备地址 | 0xA0（写）/ 0xA1（读） |
| 写入延迟 | 10ms/字节 |

**EEPROM 数据布局（256 字节）：**

| 地址范围 | 数据 | 说明 |
|----------|------|------|
| 0 | `not_first_time` 标志 | 首次使用标志（0x55 = 已初始化） |
| 1-6 | 管理员密码 | 6 位 ASCII，默认 "888888" |
| 7-12 | 开门密码 | 6 位 ASCII，默认 "123456" |
| 13-28 | 卡片 0 | 1字节标志 + 4字节 UID + 填充 |
| 29-44 | 卡片 1 | 1字节标志 + 4字节 UID + 填充 |
| 45-60 | 卡片 2 | 1字节标志 + 4字节 UID + 填充 |
| 255 | 存活标志 | 0x55（用于检测 EEPROM 是否正常） |

**首次使用初始化：** 若 `not_first_time != 0x55`，自动清零 EEPROM，写入默认密码和空卡片数据。

**关键函数：**
- `AT24CXX_Init()` — 初始化 I2C 总线
- `AT24CXX_ReadOneByte(ReadAddr)` — 读单字节
- `AT24CXX_WriteOneByte(WriteAddr, DataToWrite)` — 写单字节（含 10ms 延迟）
- `AT24CXX_Read(ReadAddr, pBuffer, NumToRead)` — 读块数据
- `AT24CXX_Write(WriteAddr, pBuffer, NumToWrite)` — 写块数据（逐字节）
- `AT24CXX_Check()` — EEPROM 在线检测（写入/读回地址 255 的标志字节）

#### 3. MFRC522 RFID 模块

| 项目 | 说明 |
|------|------|
| 芯片 | MFRC522 (NXP) |
| 通信 | 软件 SPI（非硬件 SPI） |
| 协议 | ISO 14443A |
| 支持卡型 | Mifare Ultralight, Mifare One S50/S70, Mifare DESFire |

**引脚连接：**

| RC522 引脚 | STM32 引脚 | 功能 |
|-----------|-----------|------|
| SDA/CS | PA4 | SPI 片选 |
| SCK | PA5 | SPI 时钟 |
| MOSI | PA6 | SPI 数据输出 |
| MISO | PA7 | SPI 数据输入 |
| RST | PB0 | 硬件复位 |

**卡片注册：** 最多注册 3 张卡片（ID 0-2），每张卡片存储 4 字节 UID + 存在标志。

**关键函数：**
- `PcdRequest(req_code, *pTagType)` — RF 场请求
- `PcdAnticoll(*pSnr)` — 防冲突，返回 4 字节 UID
- `PcdSelect(*pSnr)` — 选卡
- `PcdAuthState(mode, addr, *pKey, *pSnr)` — 密钥认证
- `WriteDataBlock(ucAddr, *pData)` — 自动处理请求-选卡-认证-写入全流程

#### 4. LCD12864 显示屏

| 项目 | 说明 |
|------|------|
| 控制器 | ST7920 兼容 |
| 分辨率 | 128x64 像素 |
| 接口 | 3 线串口模式 |
| 显示 | 4 行 x 8 列中文字符 |

**引脚连接：**

| LCD 引脚 | STM32 引脚 | 功能 |
|---------|-----------|------|
| CS (片选) | PB8 | 启用/禁用 |
| CLK (时钟) | PB9 | 串行时钟 |
| SID (数据) | PB10 | 串行数据 |

**串口协议：** 每字节以 `0xF8`（命令）或 `0xFA`（数据）为前缀，高 4 位 + 低 4 位分两次发送。

**显示内容：** 4 行 x 8 列中文字符，DDRAM 地址映射：行 0=0x80-0x87, 行 1=0x90-0x97, 行 2=0x88-0x8F, 行 3=0x98-0x9F。

**关键函数：**
- `lcd_draw_str(column, row, str)` — 指定位置显示字符串
- `lcd_draw_num(column, row, num)` — 指定位置显示数字
- `lcd_clear()` — 清屏（图形模式）
- `lcd_draw_dots(x, y, color)` — 像素级绘制

#### 5. 4x4 矩阵键盘

| 项目 | 说明 |
|------|------|
| 类型 | 4x4 矩阵键盘（16 键） |
| 接口 | 直接 GPIO |
| 扫描 | TIM2 定时器驱动，20ms 周期 |

**引脚连接：**

| 列 | STM32 引脚 | 行 | STM32 引脚 |
|----|-----------|-----|-----------|
| COL_1 | PB15 | ROW_1 | PA15 |
| COL_2 | PB14 | ROW_2 | PB3 |
| COL_3 | PB13 | ROW_3 | PB4 |
| COL_4 | PB12 | ROW_4 | PB5 |

**按键映射：**

| 键位 | 功能 | 键位 | 功能 |
|------|------|------|------|
| 1 | 数字 "1" | 7 | 数字 "7" |
| 2 | 数字 "2" | 8 | 数字 "8" |
| 3 | 数字 "3" | 9 | 数字 "9" |
| 4 | 数字 "4" | * | 星号 |
| 5 | 数字 "5" | 0 | 数字 "0" |
| 6 | 数字 "6" | # | 井号 |
| + | 上翻 | Enter | 确认 |
| - | 下翻 | Back | 返回 |

**消抖机制：** 扫描函数实现按键释放追踪，同一按键只触发一次。

#### 6. 通用 GPIO 模块 (General_Module)

通用 GPIO 封装，用于控制蜂鸣器和继电器：

| 设备 | 引脚 | 模式 | 说明 |
|------|------|------|------|
| 蜂鸣器 | PB1 | 输出（低电平有效） | 高=关闭，低=开启（错误反馈） |
| 继电器 | PB11 | 输出 | 高=吸合=开门，500ms 脉冲 |

#### 7. 软件 I2C 总线 (IIC)

| 信号 | STM32 引脚 | 模式 |
|------|-----------|------|
| SCL | PB6 | 推挽输出 |
| SDA | PB7 | 开漏输出 / 上拉输入（动态切换） |

通过 `SDA_IN()`/`SDA_OUT()` 动态切换 PB7 方向，实现 I2C 通信。用于连接 AT24C02 EEPROM。

### 网络通信模块

系统支持两种网络连接方式，通过编译时 `#define COMM_MODE` 切换：

#### 方式一：ESP32-S3 WiFi 模块

| 项目 | 说明 |
|------|------|
| 芯片 | ESP32-S3（目录名 ESP8266，实际为 ESP32-S3） |
| 框架 | Arduino (PlatformIO) |
| MQTT 库 | PubSubClient |
| UART 连接 | GPIO17(RX) ↔ STM32 PA9(TX), GPIO18(TX) ↔ STM32 PA10(RX) |
| 波特率 | 9600 baud, 8N1 |

**MQTT 主题：**
- 订阅：`door/{device_id}/command` — 接收 `OPEN_DOOR` 指令
- 发布：`door/{device_id}/status` — 上报 `ONLINE`、`OK`、`PWD_OK`、`FP_OK`、`CARD_OK`

**工作流程：**
1. 连接 WiFi → 连接 MQTT Broker
2. 订阅命令主题，每 30 秒发布 `ONLINE` 心跳
3. 收到 MQTT 指令 → 通过 UART 转发给 STM32
4. 读取 STM32 UART 响应 → 发布到 MQTT 状态主题

#### 方式二：W5500 以太网模块

| 项目 | 说明 |
|------|------|
| 芯片 | WIZnet W5500（硬件 TCP/IP 协议栈） |
| 通信 | 软件 SPI |
| MQTT | 自实现 MQTT v3.1.1 客户端（无外部库） |
| 缓冲区 | 256 字节 TX + 256 字节 RX |

**引脚连接：**

| W5500 引脚 | STM32 引脚 | 功能 |
|-----------|-----------|------|
| SCK | PA1 | SPI 时钟 |
| MISO | PA8 | SPI 数据输入 |
| MOSI | PA11 | SPI 数据输出 |
| CS | PA12 | 片选 |
| RST | PC13 | 硬件复位 |

**MQTT 实现：** 自定义包构建（CONNECT/SUBSCRIBE/PUBLISH/PINGREQ），QoS 0，Keepalive 60s。支持 Socket 重连（含 W5500 硬件复位重试 3 次）。

**切换步骤：**
1. 连接 W5500 模块（PA1/PA8/PA11/PA12/PC13）
2. 断开 ESP32-S3 UART 线（PA9/PA10）
3. 修改 `main.c` 和 `menu.c` 中的 `COMM_MODE` 为 `COMM_MODE_W5500`
4. 配置网络参数（MAC、IP、网关、子网掩码、MQTT Broker IP）

### STM32 菜单系统

LCD12864 显示多级菜单，通过矩阵键盘导航：

| 页面 | 功能 |
|------|------|
| 主页 (disp=0, sub=0) | "智能电子密码锁" + 6 位密码输入 |
| 管理员登录 (disp=0, sub=1) | 输入管理员密码进入管理菜单 |
| 管理菜单 (disp=1) | 指纹管理 / 密码管理 / 卡片管理 |
| 指纹管理 (disp=2) | 添加指纹(ID 0-4) / 删除指纹 |
| 密码管理 (disp=3) | 修改开门密码 / 修改管理员密码 |
| 卡片管理 (disp=4) | 添加卡片(ID 0-2) / 删除卡片 |

**导航按键：** "+" 上翻, "-" 下翻, Enter 确认, Back 返回

**主页面认证触发（始终活跃）：**
- 蓝牙解锁：USART1 接收匹配开门密码
- RFID 刷卡：检测到匹配已注册卡片
- 指纹识别：PA0 检测到手指 → AS608 采集 → 1:N 搜索
- 密码输入：6 位数字匹配开门密码

### 完整引脚分配

| STM32 引脚 | 用途 | 模块 |
|-----------|------|------|
| PA0 | AS608 手指检测（输入） | 指纹 |
| PA1 | W5500 SCK (软件 SPI) | 以太网 |
| PA2 | USART2 TX → AS608 | 指纹 |
| PA3 | USART2 RX ← AS608 | 指纹 |
| PA4 | RC522 CS (软件 SPI) | RFID |
| PA5 | RC522 SCK | RFID |
| PA6 | RC522 MOSI | RFID |
| PA7 | RC522 MISO | RFID |
| PA8 | W5500 MISO | 以太网 |
| PA9 | USART1 TX (printf/ESP32-S3) | 串口 |
| PA10 | USART1 RX (ESP32-S3 指令) | 串口 |
| PA11 | W5500 MOSI | 以太网 |
| PA12 | W5500 CS | 以太网 |
| PA15 | 矩阵键盘 ROW_1 | 键盘 |
| PB0 | RC522 RST | RFID |
| PB1 | 蜂鸣器（低电平有效） | GPIO |
| PB3 | 矩阵键盘 ROW_2 | 键盘 |
| PB4 | 矩阵键盘 ROW_3 | 键盘 |
| PB5 | 矩阵键盘 ROW_4 | 键盘 |
| PB6 | I2C SCL (AT24C02) | EEPROM |
| PB7 | I2C SDA (AT24C02) | EEPROM |
| PB8 | LCD12864 CS | 显示屏 |
| PB9 | LCD12864 CLK | 显示屏 |
| PB10 | LCD12864 SID | 显示屏 |
| PB11 | 继电器（电磁锁） | GPIO |
| PB12 | 矩阵键盘 COL_4 | 键盘 |
| PB13 | 矩阵键盘 COL_3 | 键盘 |
| PB14 | 矩阵键盘 COL_2 | 键盘 |
| PB15 | 矩阵键盘 COL_1 | 键盘 |
| PC13 | W5500 RST | 以太网 |

### 串口配置

| 串口 | 引脚 | 波特率 | 用途 |
|------|------|--------|------|
| USART1 | PA9(TX), PA10(RX) | 9600 | printf 重定向 + ESP32-S3 通信 |
| USART2 | PA2(TX), PA3(RX) | 57600 | AS608 指纹模块通信 |

### 定时器配置

| 定时器 | 周期 | 用途 |
|--------|------|------|
| TIM2 | 20ms (arr=1999, psc=719) | 键盘扫描 + 系统时钟计数 |
| TIM3 | 10ms (arr=99, psc=7199) | USART2 帧超时检测（AS608 数据包结束判断） |

### 串口桥接脚本

`serial_mqtt_bridge.py` — 开发调试用，桥接 CH340 USB 串口和 MQTT：

- 自动检测 CH340 串口（或手动选择）
- 订阅 `door/{DEVICE_ID}/command`，转发 `OPEN_DOOR\n` 到 STM32
- 读取 STM32 响应（`OK`/`PWD_OK`/`FP_OK`/`CARD_OK`），发布到 MQTT 状态主题
- 每 30 秒发布 `ONLINE` 心跳
- 支持手动输入命令

---

## API 文档

### 认证接口
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 用户登录（限流 5 次/60s） | 公开 |
| POST | `/api/auth/register` | 用户注册 | 公开 |
| POST | `/api/auth/logout` | 退出登录（Token 黑名单） | 已认证 |
| PUT | `/api/auth/password` | 修改密码 | 已认证 |

### 用户管理（仅管理员）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/users` | 用户列表（分页、搜索、角色筛选） |
| POST | `/api/users` | 创建用户 |
| DELETE | `/api/users/{user_id}` | 删除用户（需先解绑） |
| GET | `/api/users/{user_id}/devices` | 查询用户绑定设备 |

### 设备管理
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/devices` | 创建设备 | 管理员 |
| GET | `/api/devices` | 设备列表（分页、搜索） | 已认证 |
| PUT | `/api/devices/{device_id}` | 更新设备 | 管理员 |
| DELETE | `/api/devices/{device_id}` | 删除设备（需先解绑） | 管理员 |
| POST | `/api/devices/{device_id}/bind` | 绑定用户到设备 | 管理员 |
| DELETE | `/api/devices/{device_id}/unbind` | 解绑用户与设备 | 管理员 |

### 门禁控制
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/doors/{device_id}/open` | 开启门禁（含权限校验） | 已认证 |
| GET | `/api/door-logs` | 查询开门日志（多维度筛选、分页） | 已认证 |

### 统计 / AI / WebSocket
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/statistics` | 获取统计数据 | 已认证 |
| POST | `/api/ai/chat` | AI 对话开门和数据查询 | 管理员 |
| WS | `/api/ws` | WebSocket 实时开门通知 | JWT 认证 |

**WebSocket 认证流程：**
1. 客户端连接后发送 `{"type": "auth", "token": "..."}`
2. 服务端验证 JWT（10 秒超时）
3. 认证成功 → 管理员收到开门通知
4. 消息格式：`{"type": "door_open", "message": "【用户名】打开了【设备名】(位置)"}`

完整 API 文档：http://localhost:8000/docs

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `SECRET_KEY` | JWT 密钥（至少 32 字符） | - | ✅ |
| `MYSQL_HOST` | MySQL 主机 | - | ✅ |
| `MYSQL_PORT` | MySQL 端口 | 3306 | ❌ |
| `MYSQL_USER` | MySQL 用户 | root | ❌ |
| `MYSQL_PASSWORD` | MySQL 密码 | - | ✅ |
| `MYSQL_DB` | 数据库名 | - | ✅ |
| `REDIS_HOST` | Redis 主机 | 127.0.0.1 | ❌ |
| `REDIS_PORT` | Redis 端口 | 6379 | ❌ |
| `REDIS_DB` | Redis 数据库 | 0 | ❌ |
| `REDIS_PASSWORD` | Redis 密码 | 无 | ❌ |
| `MQTT_BROKER_HOST` | MQTT Broker 主机 | 127.0.0.1 | ❌ |
| `MQTT_BROKER_PORT` | MQTT Broker 端口 | 1883 | ❌ |
| `MQTT_USERNAME` | MQTT 用户名 | 空 | ❌ |
| `MQTT_PASSWORD` | MQTT 密码 | 空 | ❌ |
| `MQTT_TOPIC_PREFIX` | MQTT 主题前缀 | door | ❌ |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 无 | ❌ |
| `AI_API_URL` | AI API 地址 | https://api.deepseek.com/v1/chat/completions | ❌ |
| `AI_MODEL` | AI 模型 | deepseek-v4-flash | ❌ |
| `AI_TIMEOUT` | AI 超时时间(秒) | 15 | ❌ |
| `AI_TEMPERATURE` | AI 温度参数 | 0.1 | ❌ |
| `ALLOWED_ORIGINS` | CORS 允许来源（逗号分隔） | * | ❌ |
| `ADMIN_USERNAME` | 管理员用户名 | admin | ❌ |
| `ADMIN_PASSWORD` | 管理员密码 | 123456 | ❌ |
| `AUTO_CREATE_ADMIN` | 自动创建管理员 | true | ❌ |

### Docker 部署注意

Docker 环境下必须使用服务名而非 localhost：
```env
MYSQL_HOST=mysql
REDIS_HOST=redis
MQTT_BROKER_HOST=mosquitto
```

本地开发使用：
```env
MYSQL_HOST=localhost
REDIS_HOST=127.0.0.1
MQTT_BROKER_HOST=127.0.0.1
```

### Docker 服务端口

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| MySQL | 3306 | 3307 | 数据库 |
| Redis | 6379 | 6379 | 缓存 |
| Mosquitto | 1883 | 1883 | MQTT Broker |
| FastAPI | 8000 | 8000 | 后端 API |
| Nginx | 80 | 80 | 前端（主入口） |

---

## 常见问题

### Docker 部署

**1. 数据库连接失败**
确保 `.env` 中使用服务名：`MYSQL_HOST=mysql`（不是 localhost）

**2. 前端页面空白**
```bash
docker-compose logs frontend          # 查看日志
docker-compose up -d --build frontend # 重新构建
```

**3. 后端 502 Bad Gateway**
```bash
docker-compose ps fastapi             # 检查服务状态
docker-compose logs fastapi           # 查看日志
docker-compose restart fastapi        # 重启
```

**4. 代码修改后生效**
```bash
docker-compose up -d --build fastapi    # 后端修改
docker-compose up -d --build frontend   # 前端修改
docker-compose up -d --build            # 全部重建
```

**5. 完全重置（清空数据）**
```bash
docker-compose down -v    # 删除数据卷
docker-compose up -d      # 重新启动
```

### 功能相关

**6. AI 功能不工作**
- 检查是否配置 `DEEPSEEK_API_KEY`
- 确认可访问 `api.deepseek.com`

**7. MQTT 连接失败**
- Docker：检查 `docker-compose ps mosquitto`
- 本地：确保 Mosquitto 已启动（`mosquitto -v`）

**8. 设备离线**
- 检查设备固件 MQTT 配置（Broker 地址、端口）
- 设备在线状态 Redis 缓存 70 秒过期，等待自动恢复

**9. 用户/设备删除失败**
需先解绑所有关联：删除用户前解绑其所有设备，删除设备前解绑所有用户

**10. 运行测试**
```bash
pytest tests/ -v                # 运行所有测试
pytest tests/test_auth.py -v    # 运行特定测试
pytest tests/ --cov=.           # 覆盖率报告
```

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 新功能描述'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 后端：PEP 8 + 类型提示
- 前端：Composition API (`<script setup>`)
- 统一响应格式：`{code, msg, data}`

### Git 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 重构
test: 测试
chore: 构建/工具变更
```

## 安全建议

生产环境部署前：
- [ ] 修改默认管理员密码
- [ ] 使用强随机 `SECRET_KEY`（至少 32 字符）
- [ ] 配置 HTTPS
- [ ] 限制 CORS 允许的域名（不使用 `*`）
- [ ] 启用 Redis 密码认证
- [ ] 定期备份数据库

生成安全的 SECRET_KEY：
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 许可证

本项目采用 MIT 许可证

## 作者

Allen

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [DeepSeek](https://deepseek.com/)
- [Eclipse Mosquitto](https://mosquitto.org/)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/)
- [STM32](https://www.st.com/)
- [PlatformIO](https://platformio.org/)

---

最后更新: 2026-05-29 | 版本: v2.1 | 许可证: MIT
