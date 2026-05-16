# 门禁管理系统 (Door Access System)

一个基于 FastAPI + Vue 3 的智能化门禁管理系统，支持多设备管理、用户权限控制、开门记录查询和 AI 智能开门功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
  - [🐳 Docker 部署（强烈推荐）](#-docker-部署强烈推荐)
  - [💻 手动部署（开发模式）](#-手动部署开发模式)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [开发规范](#开发规范)
- [安全建议](#安全建议)
- [监控与日志](#监控与日志)
- [贡献指南](#贡献指南)

## ✨ 功能特性

### 用户管理
- ✅ JWT Token 认证，支持登录/退出
- ✅ 用户角色管理（管理员/普通用户）
- ✅ 用户 CRUD 操作
- ✅ 密码 bcrypt 加密存储（72字节限制处理）
- ✅ Token 黑名单机制（Redis）
- ✅ **修改密码功能**（验证原密码 + 新密码强度检查）

### 设备管理
- ✅ 设备增删改查
- ✅ 设备与用户绑定/解绑
- ✅ Redis 缓存优化（60秒）
- ✅ 按权限过滤设备列表
- ✅ 设备名称模糊搜索

### 门禁控制
- ✅ 用户开门接口
- ✅ 权限验证（管理员/绑定用户）
- ✅ 开门日志自动记录
- ✅ 多维度日志查询（时间/状态/设备）
- ✅ 分页展示

### 统计分析
- ✅ 首页数据统计
- ✅ 按角色展示不同数据
- ✅ Redis 缓存优化（180秒）

### AI 智能助手
- ✅ 自然语言控制开门
- ✅ DeepSeek AI 集成（deepseek-v4-flash）
- ✅ 智能设备识别
- ✅ 对话上下文管理（Redis 存储，900秒过期）

### WebSocket 实时通信
- ✅ 实时门禁状态推送
- ✅ 双向通信支持
- ✅ 自动重连机制

### 系统优化
- ✅ **应用生命周期管理**（FastAPI lifespan）
- ✅ **自动管理员初始化**（启动时自动创建默认管理员）
- ✅ **自动数据库初始化**（自动建库 + 建表，无需手动操作）
- ✅ **日志优化**（结构化日志输出，减少冗余）
- ✅ **健康检查接口**（`/health` 端点）
- ✅ **SQLAlchemy 日志优化**（生产环境关闭 SQL 调试日志）

### 前端界面
- ✅ Vue 3.5 + Element Plus 2.14
- ✅ Pinia 状态管理
- ✅ Vue Router 路由管理
- ✅ 响应式设计
- ✅ 实时数据展示
- ✅ 友好的用户体验

## 🛠️ 技术栈

### 后端
- **Web 框架**: FastAPI 0.104.1
- **数据库 ORM**: SQLAlchemy 2.0.23
- **数据库驱动**: PyMySQL 1.1.0
- **缓存**: Redis 5.0.1
- **认证**: JWT (python-jose 3.3.0)
- **密码加密**: bcrypt 4.0.1 + passlib 1.7.4
- **异步服务器**: Uvicorn 0.24.0
- **WebSocket**: websockets >=10.0
- **HTTP 客户端**: requests 2.31.0
- **环境变量**: python-dotenv 1.0.0
- **数据验证**: Pydantic 2.5.0

### 前端
- **框架**: Vue 3.5
- **UI 组件库**: Element Plus 2.14
- **图标库**: @element-plus/icons-vue 2.3.2
- **状态管理**: Pinia 3.0.4
- **路由管理**: Vue Router 4.6.4
- **HTTP 客户端**: Axios 1.16.0
- **构建工具**: Vite 8.0.10

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│           前端 (Vue 3 + Element)         │
│  ┌────────┬────────┬──────┬──────┐      │
│  │ 登录   │ 用户   │ 设备 │ 日志 │      │
│  └────────┴────────┴──────┴──────┘      │
└──────────────┬──────────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────────┐
│         后端 (FastAPI)                   │
│  ┌─────────────────────────────────┐    │
│  │      API Router (路由层)         │    │
│  ├─────────────────────────────────┤    │
│  │     Services (业务逻辑层)        │    │
│  ├─────────────────────────────────┤    │
│  │    Models & Schemas (数据层)     │    │
│  └─────────────────────────────────┘    │
└──────┬──────────────┬──────────────────┘
       │              │
  ┌────▼────┐   ┌────▼────┐
  │  MySQL  │   │  Redis  │
  │ 数据库   │   │  缓存    │
  └─────────┘   └─────────┘
```

## 🚀 快速开始

### 前置要求

**推荐使用 Docker 部署（最简单）：**
- Docker & Docker Compose

**或者手动部署需要：**
- Python 3.8+
- MySQL 5.7+ 或 8.0+
- Redis 6.0+
- Node.js 16+ & npm (仅前端开发时需要)

---

### 🐳 Docker 部署（强烈推荐）

使用 Docker Compose 一键部署所有服务（MySQL + Redis + Backend + Frontend），这是最简单、最推荐的部署方式。

#### 1. 克隆项目
```bash
git clone <repository-url>
cd door_access_system
```

#### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并修改配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，**注意 Docker 环境下数据库和 Redis 的主机名需要使用服务名**：
```env
# ==================== JWT 认证配置 ====================
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# ==================== 管理员初始化配置 ====================
ADMIN_USERNAME=admin
ADMIN_PASSWORD=123456
AUTO_CREATE_ADMIN=true

# ==================== AI 配置 ====================
# 注意：AI 功能是可选的，未配置此项不影响系统启动
# 如需使用 AI 智能助手功能，请配置以下参数
DEEPSEEK_API_KEY=your-deepseek-api-key-here
AI_API_URL=https://api.deepseek.com/v1/chat/completions
AI_MODEL=deepseek-v4-flash
AI_TIMEOUT=15
AI_TEMPERATURE=0.1

# ==================== 数据库配置 ====================
# ⚠️ Docker 环境中必须使用服务名 "mysql"，不能用 "localhost" 或 "127.0.0.1"
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DB=door_access_system

# ==================== Redis 配置 ====================
# ⚠️ Docker 环境中必须使用服务名 "redis"，不能用 "localhost" 或 "127.0.0.1"
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# ==================== CORS 跨域配置 ====================
# * 表示允许所有来源访问（开发/测试环境推荐）
# 生产环境建议指定具体域名，如：http://your-domain.com
ALLOWED_ORIGINS=*
```

**⚠️ 安全提示：**
- `SECRET_KEY` 应使用强随机字符串
- 生产环境请修改默认管理员密码
- 不要将 `.env` 文件提交到版本控制系统

#### 3. 构建前端（重要！）

在启动 Docker 之前，需要先构建前端项目：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 返回项目根目录
cd ..
```

这会在 `frontend/dist` 目录生成静态文件，Docker 会将其复制到 Nginx 容器中。

#### 4. 启动所有服务
```bash
docker-compose up -d
```

首次启动会自动：
- ✅ 创建 MySQL 数据库和表结构
- ✅ 启动 Redis 缓存服务
- ✅ 启动后端 FastAPI 服务
- ✅ 构建并启动前端 Vue 应用
- ✅ 创建默认管理员账户（用户名: `admin`, 密码: `123456`）
- ⚠️ **请在首次登录后立即修改密码！**

#### 5. 查看服务状态
```bash
docker-compose ps
```

#### 6. 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi
docker-compose logs -f frontend
docker-compose logs -f mysql
```

#### 4. 停止服务
```
docker-compose down
```

**💡 重要提示：**
- 如果你修改了前端代码，需要重新构建前端并重启容器：
  ```bash
  cd frontend && npm run build && cd ..
  docker-compose up -d --build frontend
  ```
- 如果只修改了后端代码，只需重启后端容器：
  ```bash
  docker-compose up -d --build fastapi
  ```

**服务访问地址：**
- 🌐 前端界面：http://localhost:80
- 🔌 后端 API：http://localhost:8000
- 📚 API 文档：http://localhost:8000/docs
- 💚 健康检查：http://localhost:8000/health
- 🗄️ MySQL：localhost:3307（外部访问端口）
- 📦 Redis：localhost:6379（外部访问端口）

**Docker 部署优势：**
- ✅ 一键部署，无需手动安装 MySQL、Redis、Python、Node.js
- ✅ 环境隔离，避免依赖冲突
- ✅ 前后端统一管理，简化运维
- ✅ 易于扩展和维护
- ✅ 生产环境推荐方案

---

### 💻 手动部署（开发模式）

如果你需要本地开发或调试，可以选择手动部署各个组件。

#### 后端安装

#### 1. 克隆项目
```bash
git clone <repository-url>
cd door_access_system
```

#### 2. 创建虚拟环境
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
复制 `.env.example` 为 `.env` 并修改配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填写你的实际配置（**本地开发环境**）：
```env
# ==================== JWT 认证配置 ====================
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# ==================== 管理员初始化配置 ====================
ADMIN_USERNAME=admin
ADMIN_PASSWORD=123456
AUTO_CREATE_ADMIN=true

# ==================== AI 配置 ====================
DEEPSEEK_API_KEY=your-deepseek-api-key
AI_API_URL=https://api.deepseek.com/v1/chat/completions
AI_MODEL=deepseek-v4-flash
AI_TIMEOUT=15
AI_TEMPERATURE=0.1

# ==================== 数据库配置 ====================
# 本地开发使用 localhost 或 127.0.0.1
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=door_access_system

# ==================== Redis 配置 ====================
# 本地开发使用 127.0.0.1
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

# ==================== CORS 跨域配置 ====================
# * 表示允许所有来源访问（方便多设备访问）
# 生产环境建议指定具体域名以提高安全性
ALLOWED_ORIGINS=*
```

**⚠️ 安全提示：**
- `SECRET_KEY` 应使用强随机字符串
- 生产环境请修改默认管理员密码
- 不要将 `.env` 文件提交到版本控制系统

#### 5. 启动 Redis
```bash
# Windows
redis-server

# Linux
sudo systemctl start redis

# Mac
brew services start redis
```

#### 6. 运行后端服务
```bash
python main.py
```

**首次启动会自动：**
- ✅ 自动创建 MySQL 数据库（如果不存在）
- ✅ 自动创建所有数据表
- ✅ 创建默认管理员账户（用户名: `admin`, 密码: `123456`）
- ⚠️ **请在首次登录后立即修改密码！**

访问 API 文档：http://127.0.0.1:8000/docs  
健康检查：http://127.0.0.1:8000/health

---

### 前端安装

#### 1. 进入前端目录
```bash
cd frontend
```

#### 2. 安装依赖
```bash
npm install
```

#### 3. 启动开发服务器
```bash
npm run dev
```

访问前端界面：http://localhost:5173

## 📁 项目结构

```
door_access_system/
├── api/                    # API 路由层
│   ├── user_api.py        # 用户管理接口
│   ├── device_api.py      # 设备管理接口
│   ├── door_api.py        # 门禁控制接口
│   ├── stat_api.py        # 统计分析接口
│   ├── ai_agent.py        # AI 助手接口
│   ├── websocket_api.py   # WebSocket 实时通信
│   └── routers.py         # 路由汇总
├── core/                   # 核心配置
│   ├── config.py          # 统一配置管理
│   └── ai_system_prompt.py # AI 系统提示词
├── database/              # 数据库相关
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── device.py      # 设备模型
│   │   ├── user_device.py # 用户设备关联
│   │   └── door_log.py    # 开门日志
│   ├── db.py              # 数据库连接
│   ├── redis.py           # Redis 连接
│   └── admin.py           # 管理员初始化
├── services/              # 业务逻辑层
│   ├── user_service.py    # 用户服务
│   ├── device_service.py  # 设备服务
│   ├── door_service.py    # 门禁服务
│   ├── stat_service.py    # 统计服务
│   ├── ai_agent_service.py # AI 代理服务
│   └── websocket_service.py # WebSocket 服务
├── schemas/               # 数据验证
│   ├── user_schema.py     # 用户 schema
│   ├── device_schema.py   # 设备 schema
│   └── door_schema.py     # 门禁 schema
├── utils/                 # 工具函数
│   ├── auth.py            # 认证工具
│   ├── response.py        # 响应封装
│   ├── logger.py          # 日志工具
│   └── exceptions.py      # 异常处理
├── frontend/              # 前端项目（Vue 3）
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   └── package.json
├── logs/                  # 日志文件
├── .env                   # 环境变量（不提交到 Git）
├── .env.example           # 环境变量示例
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile.backend     # 后端 Docker 镜像
├── Dockerfile.frontend    # 前端 Docker 镜像
├── main.py                # 应用入口
├── requirements.txt       # Python 依赖
└── README.md              # 项目文档
```

## 📖 API 文档

### RESTful 设计规范

本项目严格遵循 **RESTful API** 设计规范：

- ✅ **资源命名**：使用名词复数形式（如 `/users`, `/devices`）
- ✅ **HTTP 方法**：正确使用 GET/POST/PUT/DELETE
- ✅ **子资源**：使用嵌套路径表示关系（如 `/devices/{id}/bind`）
- ✅ **无状态**：通过 JWT Token 进行身份验证
- ✅ **统一接口**：所有响应格式统一为 `{code, msg, data}`

#### HTTP 方法说明

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 获取资源 | `GET /users` - 获取用户列表 |
| POST | 创建资源 | `POST /users` - 创建新用户 |
| PUT | 更新资源 | `PUT /devices/1` - 更新设备1 |
| DELETE | 删除资源 | `DELETE /users/1` - 删除用户1 |

### 认证接口

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/auth/login` | 用户登录 | 公开 |
| POST | `/auth/logout` | 退出登录 | 已认证 |
| PUT | `/auth/password` | **修改密码** | 已认证 |

### 用户管理（仅管理员）

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/users` | 获取用户列表 |
| POST | `/users` | 创建用户 |
| DELETE | `/users/{user_id}` | 删除用户 |
| GET | `/users/{user_id}/devices` | 查询用户绑定设备 |

### 设备管理

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/devices` | 创建设备 | 管理员 |
| GET | `/devices` | 获取设备列表 | 已认证 |
| PUT | `/devices/{device_id}` | 更新设备 | 管理员 |
| DELETE | `/devices/{device_id}` | 删除设备 | 管理员 |
| POST | `/devices/{device_id}/bind` | 绑定用户到设备 | 管理员 |
| DELETE | `/devices/{device_id}/unbind?user_id={user_id}` | 解绑用户与设备 | 管理员 |

### 门禁控制

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/doors/{device_id}/open` | 开启门禁 | 已认证 |
| GET | `/door-logs` | 查询开门日志 | 已认证 |

### 统计分析

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/statistics` | 获取统计数据 | 已认证 |

### AI 助手

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/ai/chat` | AI 对话开门 | 管理员 |

### WebSocket 实时通信

| 路径 | 描述 | 权限 |
|------|------|------|
| `ws://127.0.0.1:8000/ws/{user_id}` | WebSocket 连接 | 已认证 |

完整 API 文档请访问：http://127.0.0.1:8000/docs

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值       | 必填 |
|--------|------|-----------|------|
| SECRET_KEY | JWT 密钥 | -         | ✅ |
| ALGORITHM | JWT 算法 | HS256     | ❌ |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 有效期(分钟) | 3600      | ❌ |
| ADMIN_USERNAME | 默认管理员用户名 | admin     | ❌ |
| ADMIN_PASSWORD | 默认管理员密码 | 123456    | ❌ |
| AUTO_CREATE_ADMIN | 自动创建管理员 | true      | ❌ |
| MYSQL_HOST | MySQL 主机地址 | -         | ✅ |
| MYSQL_PORT | MySQL 端口 | 3306      | ❌ |
| MYSQL_USER | MySQL 用户名 | root      | ❌ |
| MYSQL_PASSWORD | MySQL 密码 | -         | ✅ |
| MYSQL_DB | 数据库名称 | -         | ✅ |
| REDIS_HOST | Redis 主机地址 | 127.0.0.1 | ❌ |
| REDIS_PORT | Redis 端口 | 6379      | ❌ |
| REDIS_DB | Redis 数据库编号 | 0         | ❌ |
| REDIS_PASSWORD | Redis 密码 | 无         | ❌ |
| DEEPSEEK_API_KEY | DeepSeek API Key | 无（可选）     | ❌ |
| ALLOWED_ORIGINS | CORS 允许来源 | *         | ❌ |

### Redis 缓存策略

| 缓存键 | 过期时间 | 说明 |
|--------|----------|------|
| `cache:device:list:user:{user_id}` | 60秒 | 设备列表缓存 |
| `stat:user:{user_id}` | 180秒 | 统计数据缓存 |
| `token:{token}` | 同Token有效期 | 活跃 Token |
| `blacklist:{token}` | 86400秒(24小时) | Token 黑名单 |
| `ai:context:{user_id}` | 900秒(15分钟) | AI 对话上下文 |

### 性能优化

- ✅ **数据库查询优化**：使用 SQLAlchemy 懒加载和预加载策略
- ✅ **Redis 多级缓存**：减少数据库压力，提升响应速度
- ✅ **异步处理**：FastAPI 原生异步支持，提高并发能力
- ✅ **连接池管理**：数据库和 Redis 连接复用
- ✅ **日志轮转**：按日期分割日志文件，避免单文件过大

## ❓ 常见问题

### 1. 应该选择 Docker 部署还是手动部署？

**推荐 Docker 部署，如果：**
- ✅ 你想要快速部署和运行系统
- ✅ 你不想手动安装 MySQL、Redis 等依赖
- ✅ 你需要在生产环境中部署
- ✅ 你希望环境隔离，避免依赖冲突

**选择手动部署，如果：**
- 💻 你需要进行本地开发和调试
- 🔧 你需要修改后端代码并实时测试
- 🐛 你需要调试具体的问题
- 📚 你想深入了解系统的每个组件

### 2. Redis 连接失败
**问题**: `Redis 未启动，将继续运行但无法退出登录`

**解决**: 
```bash
# 确保 Redis 服务正在运行
redis-server
# 或
sudo systemctl start redis
```

### 3. 数据库连接失败
**问题**: `Can't connect to MySQL server`

**解决**:
- 检查 MySQL 服务是否启动
- 确认 `.env` 中的数据库配置正确
- **注意**：项目启动时会自动创建数据库，无需手动执行 `CREATE DATABASE`

### 4. bcrypt 兼容性问题
**问题**: `AttributeError: module 'bcrypt' has no attribute '__about__'`

**解决**:
```bash
pip install bcrypt==4.0.1
```

### 5. 密码长度限制
**问题**: `密码过长`

**说明**: bcrypt 限制密码最多 72 字节，已在代码中处理。

### 6. CORS 跨域问题
**解决**: 后端已配置 CORS，可通过 `ALLOWED_ORIGINS` 环境变量配置允许的域名。

### 7. 重复日志问题
**问题**: 开发模式下日志重复输出

**解决**: 已使用 FastAPI lifespan 机制优化，确保初始化代码只执行一次。

### 8. 如何重置数据库

**方法 1**: 在 `main.py` 的 `lifespan` 中临时启用
```
# 在 main.py 的 lifespan 函数中取消注释
drop_all_tables()  # 删除所有表
init_database()    # 重新创建表和初始化管理员
```

**方法 2**: 使用 Python 命令
```bash
python -c "from database.db import Base, engine; Base.metadata.drop_all(engine)"
```

⚠️ **警告**: 这会删除所有数据，请谨慎操作！重启后会自动重建空表和管理员账户。

### 9. Docker 部署注意事项

**问题**: 容器内无法连接数据库或 Redis

**解决**: 
- 在 `.env` 文件中，Docker 环境下必须使用服务名而非 IP：
  ```env
  MYSQL_HOST=mysql    # 而不是 127.0.0.1
  REDIS_HOST=redis    # 而不是 127.0.0.1
  ```
- 确保 docker-compose.yml 中的服务名称与配置一致

### 10. WebSocket 连接失败

**问题**: WebSocket 连接被拒绝

**解决**:
- 确认后端服务已启动且支持 WebSocket（uvicorn[standard]）
- 检查防火墙设置，确保 8000 端口开放
- 前端使用正确的 WebSocket URL：`ws://127.0.0.1:8000/ws/{user_id}`

### 11. 前端跨域问题

**问题**: 前端请求后端 API 出现 CORS 错误

**解决**: 
- 默认配置已允许所有来源访问（`ALLOWED_ORIGINS=*`）
- 如需限制特定域名，修改 `.env` 中的 `ALLOWED_ORIGINS`
- 多个地址用逗号分隔：`http://localhost:5173,http://192.168.1.100`
- 重启后端服务使配置生效

## 📝 开发规范

### 代码风格
- 遵循 PEP 8 Python 编码规范
- 使用类型提示 (Type Hints)
- 函数和类添加文档字符串
- 使用中文注释说明业务逻辑

### Git 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响代码运行的变动）
refactor: 重构（既不是新增功能，也不是修改bug的代码变动）
test: 测试（添加测试或更正现有测试）
chore: 构建过程或辅助工具的变动
perf: 性能优化
```

### 分支管理
- `main`: 主分支，用于生产环境
- `develop`: 开发分支，用于日常开发
- `feature/*`: 功能分支，用于开发新功能
- `hotfix/*`: 修复分支，用于紧急修复

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🔐 安全建议

### 生产环境部署检查清单

- [ ] 修改默认管理员密码
- [ ] 使用强随机 `SECRET_KEY`（至少32字符）
- [ ] 配置 HTTPS（使用 Nginx 反向代理）
- [ ] 生产环境建议限制 CORS 允许的域名（不要使用 `*`）
- [ ] 启用 Redis 密码认证
- [ ] 定期备份数据库
- [ ] 配置日志轮转和监控
- [ ] 关闭调试模式（`reload=False`）
- [ ] 使用环境变量管理敏感信息
- [ ] 定期更新依赖包版本

### 生成安全的 SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📊 监控与日志

### 日志管理

- **日志位置**: `logs/` 目录
- **日志格式**: 按日期分割（`app.log.YYYY-MM-DD`）
- **日志级别**: INFO（生产环境）、DEBUG（开发环境）
- **记录内容**:
  - HTTP 请求方法、路径、状态码、耗时
  - 客户端 IP 地址
  - 错误信息和堆栈跟踪
  - 系统启动/关闭事件

### 健康检查

```bash
# 检查服务状态
curl http://127.0.0.1:8000/health

# 预期响应
{"status": "healthy", "service": "door_access_system"}
```

### 性能监控建议

- 使用 Prometheus + Grafana 监控系统指标
- 配置告警规则（CPU、内存、响应时间）
- 定期分析慢查询日志
- 监控 Redis 缓存命中率

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- ALLen

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [DeepSeek](https://deepseek.com/)

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 [Issue](https://github.com/your-repo/door_access_system/issues)
- 发送邮件至：your-email@example.com

---

**最后更新**: 2026-05-16
