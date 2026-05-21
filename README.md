# 门禁管理系统 (Door Access System)

一个基于 FastAPI + Vue 3 的智能化门禁管理系统，支持多设备管理、用户权限控制、开门记录查询和 AI 智能开门功能。

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg?logo=fastapi)
![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg?logo=vue.js&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg?logo=docker&logoColor=white)

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)

## 🏗️ 系统架构

### Docker 部署架构

```
┌─────────────────────────────────────────────┐
│           客户端浏览器                        │
└──────────────┬──────────────────────────────┘
               │ HTTP/WS
┌──────────────▼──────────────────────────────┐
│     Nginx (frontend:80)                     │
│  - 静态文件服务 (Vue 应用)                    │
│  - API 反向代理 (/api/ → fastapi:8000)      │
│  - WebSocket 代理 (/api/ws → fastapi:8000)  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│     FastAPI (fastapi:8000)                  │
│  - RESTful API                               │
│  - WebSocket 服务                            │
│  - 业务逻辑处理                              │
└──┬──────────────┬───────────────────────────┘
   │              │
┌──▼────┐   ┌────▼────┐
│ MySQL │   │  Redis  │
│:3306  │   │ :6379   │
└───────┘   └─────────┘
```

**服务说明：**
- **mysql**: MySQL 8.0 数据库，外部访问端口 3307
- **redis**: Redis 6 缓存服务，端口 6379
- **fastapi**: FastAPI 后端服务，端口 8000
- **frontend**: Nginx 前端服务，端口 80（主入口）

**数据流向：**
1. 用户访问 http://localhost → Nginx 提供 Vue 应用
2. 前端请求 `/api/*` → Nginx 反向代理到 FastAPI
3. WebSocket 连接 `/api/ws` → Nginx 代理到 FastAPI
4. FastAPI 读写 MySQL 和 Redis

---

## ✨ 功能特性

### 核心功能
- ✅ **用户认证**：JWT Token 认证，支持登录/注册/退出/修改密码
- ✅ **角色权限**：管理员和普通用户两级权限控制（RBAC）
- ✅ **设备管理**：设备增删改查、用户绑定/解绑
- ✅ **门禁控制**：开门操作、权限验证、日志自动记录
- ✅ **数据统计**：用户数、设备数、今日开门次数统计
- ✅ **开门日志**：多维度查询（时间/状态/设备/用户），分页展示，时间倒序

### 高级功能
- ✅ **AI 智能助手**：自然语言控制开门（DeepSeek AI 集成）
  - 支持学校场景：设备编号（001、002...）+ 位置识别
  - 多轮对话上下文记忆（Redis 存储，15分钟过期）
  - 数据查询：今日开门记录、设备列表、设备状态等
- ✅ **WebSocket**：实时门禁状态推送（管理员接收通知）
- ✅ **Redis 缓存**：设备列表（60秒）、统计数据（180秒）、AI 对话上下文（900秒）
- ✅ **自动初始化**：启动时自动创建数据库、表结构和默认管理员

### 前端界面
- 📊 **仪表盘**：欢迎横幅、实时时钟、统计数据卡片、快捷操作、最近开门记录
- 👥 **用户管理**：用户列表、搜索筛选、创建/删除用户、查看绑定设备、设备绑定/解绑
- 🔧 **设备管理**：设备列表、搜索筛选、新增/编辑/删除设备、绑定用户
- 🚪 **门禁控制**：快速开门、选择设备
- 📝 **开门日志**：日志查询、多维度筛选（用户/设备/状态/时间范围）、分页
- 💬 **AI 助手**：悬浮按钮、对话式开门和数据查询

## 🛠️ 技术栈

### 后端
- **Web 框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0.23 + PyMySQL 1.1.0
- **缓存**: Redis 5.0.1
- **认证**: JWT (python-jose 3.3.0) + bcrypt 4.0.1 + passlib 1.7.4
- **异步服务器**: Uvicorn 0.24.0 (standard)
- **WebSocket**: websockets >=10.0
- **其他**: Pydantic 2.5.0, requests 2.31.0, python-dotenv 1.0.0

### 前端
- **框架**: Vue 3.5 + Vite 8.0.10
- **UI 组件**: Element Plus 2.14 + @element-plus/icons-vue 2.3.2
- **路由**: Vue Router 4.6.4
- **HTTP**: Axios 1.16.0

### 测试
- pytest 7.4.3 + httpx 0.25.2 + pytest-cov 4.1.0 + pytest-asyncio 0.21.1

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

使用 Docker Compose 一键部署所有服务（MySQL + Redis + Backend + Frontend），这是最简单、最推荐的部署方式。

#### 1. 克隆项目
```bash
git clone <repository-url>
cd door_access_system
```

#### 2. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，**注意 Docker 环境下数据库和 Redis 的主机名必须使用服务名**：
```env
# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=123456
AUTO_CREATE_ADMIN=true

# 数据库配置（⚠️ Docker 环境必须使用服务名 "mysql"）
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DB=door_access_system

# Redis 配置（⚠️ Docker 环境必须使用服务名 "redis"）
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# CORS 配置（* 表示允许所有来源，生产环境建议指定具体域名）
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

首次启动会自动：
- ✅ 构建后端镜像（安装 Python 依赖）
- ✅ 构建前端镜像（安装 Node.js 依赖并构建 Vue 项目）
- ✅ 创建 MySQL 数据库和表结构
- ✅ 创建默认管理员账户（admin/123456）
- ✅ 启动所有服务（MySQL、Redis、Backend、Frontend）

> 💡 **优势**：Dockerfile.frontend 会在容器内自动执行 `npm install` 和 `npm run build`，无需手动构建前端！

#### 4. 查看服务状态
```bash
# 查看所有服务运行状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi    # 后端日志
docker-compose logs -f frontend   # 前端日志
docker-compose logs -f mysql      # 数据库日志
```

#### 5. 访问系统
| 服务 | 访问地址 | 说明 |
|------|---------|------|
| 🌐 前端界面 | http://localhost | Nginx 托管的 Vue 应用 |
| 🔌 后端 API | http://localhost:8000 | FastAPI 服务 |
| 📚 API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| 💚 健康检查 | http://localhost:8000/health | 服务健康状态 |
| 🗄️ MySQL | localhost:3307 | 外部访问端口（容器内 3306） |
| 📦 Redis | localhost:6379 | Redis 缓存服务 |

**默认管理员账号**：用户名 `admin`，密码 `123456`（⚠️ 首次登录后请立即修改密码）

#### 6. 常用操作
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（会清空数据库）
docker-compose down -v

# 重启特定服务
docker-compose restart fastapi

# 重建并启动服务（代码修改后）
docker-compose up -d --build

# 单独重建后端
docker-compose up -d --build fastapi

# 单独重建前端
docker-compose up -d --build frontend
```

### 方式二：手动部署（开发模式）

如果你需要本地开发或调试，可以选择手动部署各个组件。

#### 后端
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置 .env 文件（MYSQL_HOST=localhost, REDIS_HOST=127.0.0.1）

# 启动 Redis
redis-server

# 运行后端
python main.py
```

访问：http://127.0.0.1:8000/docs

#### 前端
```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

## 📖 API 文档

### 认证接口
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 用户登录 | 公开 |
| POST | `/api/auth/register` | 用户注册 | 公开 |
| POST | `/api/auth/logout` | 退出登录 | 已认证 |
| PUT | `/api/auth/password` | 修改密码 | 已认证 |

### 用户管理（仅管理员）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/users` | 获取用户列表（支持分页、用户名搜索） |
| POST | `/api/users` | 创建用户 |
| DELETE | `/api/users/{user_id}` | 删除用户（需先解绑设备） |
| GET | `/api/users/{user_id}/devices` | 查询用户绑定设备 |

### 设备管理
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/devices` | 创建设备 | 管理员 |
| GET | `/api/devices` | 获取设备列表（支持分页、名称搜索） | 已认证 |
| PUT | `/api/devices/{device_id}` | 更新设备 | 管理员 |
| DELETE | `/api/devices/{device_id}` | 删除设备（需先解绑用户） | 管理员 |
| POST | `/api/devices/{device_id}/bind` | 绑定用户到设备 | 管理员 |
| DELETE | `/api/devices/{device_id}/unbind?user_id={id}` | 解绑用户与设备 | 管理员 |

### 门禁控制
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/doors/{device_id}/open` | 开启门禁 | 已认证 |
| GET | `/api/door-logs` | 查询开门日志（支持多维度筛选、分页） | 已认证 |

### 统计分析
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/api/statistics` | 获取统计数据（用户总数、设备总数、今日开门次数） | 已认证 |

### AI 助手
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/api/ai/chat` | AI 对话开门和数据查询 | 管理员 |

### WebSocket
- 连接地址：`ws://localhost:8000/api/ws?token={token}`
- 功能：实时接收开门通知（仅管理员）
- 消息格式：`{"type": "door_open", "message": "【用户名】打开了【设备名】(位置)"}`

完整 API 文档：http://localhost:8000/docs

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| SECRET_KEY | JWT 密钥 | - | ✅ |
| MYSQL_HOST | MySQL 主机 | - | ✅ |
| MYSQL_PASSWORD | MySQL 密码 | - | ✅ |
| MYSQL_DB | 数据库名 | - | ✅ |
| REDIS_HOST | Redis 主机 | 127.0.0.1 | ❌ |
| DEEPSEEK_API_KEY | DeepSeek API Key | 无 | ❌ |
| ALLOWED_ORIGINS | CORS 允许来源 | * | ❌ |

### 数据库表结构

**user（用户表）**
- id, username（唯一）, password（bcrypt加密）, role（admin/user）, created_at

**device（设备表）**
- id, name, status（online/offline）, location, created_at, updated_at

**user_device（用户设备关联表）**
- id, user_id（外键）, device_id（外键）

**door_log（开门日志表）**
- id, user_id（外键）, device_id（外键）, action, status, time

### Redis 缓存策略

| 缓存键 | 过期时间 | 说明 |
|--------|----------|------|
| `cache:device:list:user:{user_id}` | 60秒 | 设备列表 |
| `stat:user:{user_id}` | 180秒 | 统计数据 |
| `ai:context:user:{user_id}` | 900秒 | AI 对话上下文 |
| `token:{token}` | 同Token有效期 | 活跃 Token |
| `blacklist:{token}` | 86400秒 | Token 黑名单 |

## ❓ 常见问题

### Docker 部署相关

#### 1. Docker 部署时数据库连接失败
**解决**：确保 `.env` 中使用服务名而非 IP：
```env
MYSQL_HOST=mysql    # 不是 localhost
REDIS_HOST=redis    # 不是 127.0.0.1
```

#### 2. 前端页面无法访问或显示空白
**原因**：Nginx 配置问题或前端构建失败  
**解决**：
```bash
# 查看前端容器日志
docker-compose logs frontend

# 重新构建前端
docker-compose up -d --build frontend
```

#### 3. 后端 API 返回 502 Bad Gateway
**原因**：Nginx 无法连接到后端服务  
**解决**：
```bash
# 检查后端服务是否正常运行
docker-compose ps fastapi

# 查看后端日志
docker-compose logs fastapi

# 重启后端服务
docker-compose restart fastapi
```

#### 4. 如何查看实时日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f fastapi    # 后端
docker-compose logs -f frontend   # 前端
docker-compose logs -f mysql      # 数据库

# 查看最近 100 行日志
docker-compose logs --tail=100 fastapi
```

#### 5. 代码修改后如何生效
```bash
# 修改后端代码后
docker-compose up -d --build fastapi

# 修改前端代码后
docker-compose up -d --build frontend

# 或者重建所有服务
docker-compose up -d --build
```

#### 6. 如何完全重置系统（清空数据）
```bash
# 停止并删除所有容器和数据卷
docker-compose down -v

# 重新启动
docker-compose up -d
```
⚠️ **警告**：这会删除所有数据库数据！

---

### 其他问题

#### 7. AI 功能不工作
**解决**：
- 检查是否配置了 `DEEPSEEK_API_KEY`
- 确认服务器可访问 `api.deepseek.com`
- 查看日志：`docker-compose logs fastapi | grep AI`

#### 8. 如何重置数据库
```bash
# 方法1：删除 Docker 卷
docker-compose down -v
docker-compose up -d

# 方法2：Python 命令
python -c "from database.db import Base, engine; Base.metadata.drop_all(engine)"
```
⚠️ 警告：这会删除所有数据！

#### 9. 运行测试
```bash
pytest tests/ -v                    # 运行所有测试
pytest tests/test_auth.py -v        # 运行特定测试
pytest tests/ --cov=.               # 生成覆盖率报告
```

#### 10. 用户删除失败
**原因**：该用户已绑定设备  
**解决**：先解绑用户与设备的关联，再删除用户

#### 11. 设备删除失败
**原因**：该设备已绑定用户  
**解决**：先解绑所有用户与该设备的关联，再删除设备

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 遵循 PEP 8 Python 编码规范
- 使用类型提示 (Type Hints)
- 统一响应格式：`{code, msg, data}`

### Git 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 重构
test: 测试
```

## 🔐 安全建议

生产环境部署前：
- [ ] 修改默认管理员密码
- [ ] 使用强随机 `SECRET_KEY`（至少32字符）
- [ ] 配置 HTTPS
- [ ] 限制 CORS 允许的域名（不使用 `*`）
- [ ] 启用 Redis 密码认证
- [ ] 定期备份数据库

生成安全的 SECRET_KEY：
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

Allen

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [DeepSeek](https://deepseek.com/)

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！

## 📞 联系方式

- 提交 [Issue](https://github.com/4139-Allen/Door_Access_System/issues)
- 邮箱：laichangjian894@gmail.com

---

**最后更新**: 2026-05-20 | **版本**: v2.0 | **许可证**: MIT
