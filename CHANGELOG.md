# Changelog

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
