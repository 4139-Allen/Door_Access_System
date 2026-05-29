# Changelog

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.1.0] - 2026-05-29

### Added
- 📡 集成 Eclipse Mosquitto MQTT Broker
- 🔌 MQTT 服务层（mqtt_service.py）
- 📤 设备状态上报处理（在线/离线/开门记录）
- 💓 设备心跳检测（70秒超时自动标记离线）
- 📝 本地开门记录支持（密码/指纹/刷卡开门）
- 🔧 串口转 MQTT 桥接脚本（serial_mqtt_bridge.py）
- 🛠️ STM32 硬件驱动（AS608 指纹、RC522 RFID、LCD12864、矩阵键盘）
- 📶 ESP8266/ESP32 MQTT 固件
- 🌐 W5500 以太网模块支持
- 📋 硬件说明文档
- 📡 MQTT 相关配置项（MQTT_BROKER_HOST, MQTT_TOPIC_PREFIX 等）

### Changed
- 🏗️ 更新系统架构图，添加 MQTT 通信层
- 📊 更新技术栈，添加 MQTT 和硬件相关内容
- 📝 更新 README 文档，完善硬件说明
- 🐳 Docker Compose 添加 Mosquitto 服务

### Fixed
- 修复设备在线状态缓存键名不一致问题

---

## [2.0.0] - 2026-05-24

### Added
- 🎨 前端界面重构，优化用户体验
- 📊 仪表盘统计卡片优化
- 🔍 搜索筛选功能增强
- 📝 日志表格组件优化

### Changed
- 🎨 UI 样式优化
- ⚡ 性能优化

---

## [1.0.0] - 2026-05-16

### Added
- 🎉 初始版本发布
- 👤 用户管理功能（登录/注册/权限控制）
- 🔧 设备管理功能（增删改查/绑定解绑）
- 🚪 门禁控制功能（开门/日志查询）
- 📊 统计分析功能（数据可视化）
- 🤖 AI 智能助手（自然语言控制开门）
- 💬 WebSocket 实时通信
- 🐳 Docker 一键部署支持
- 🗄️ 自动数据库初始化（建库+建表）
- 👑 自动管理员账户创建
- 🔒 JWT Token 认证 + Redis 黑名单
- 📝 完整的 API 文档（Swagger UI）
- 🎨 Vue 3 + Element Plus 前端界面
- 📱 响应式设计，支持多端访问
- 📋 详细的 README 文档
- ⚙️ 环境变量配置管理
- 🔍 健康检查接口

### Changed
- 优化跨域配置，默认允许所有来源
- 改进错误提示信息，更加友好清晰
- 优化日志输出，结构化展示

### Fixed
- 修复 bcrypt 与 passlib 版本兼容性问题
- 修复 FastAPI CORS 配置缺失问题
- 修复 SQLAlchemy DateTime 默认值问题
- 优化数据库连接池配置

### Security
- ✅ 密码 bcrypt 加密存储
- ✅ JWT Token 安全认证
- ✅ Redis Token 黑名单机制
- ✅ .env 文件不提交到 Git
- ✅ 敏感信息环境变量管理

---

## 版本说明

- **Added**：新增功能
- **Changed**：功能变更
- **Deprecated**：即将废弃的功能
- **Removed**：已移除的功能
- **Fixed**：Bug 修复
- **Security**：安全相关改进
