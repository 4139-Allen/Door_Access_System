"""
项目配置文件
集中管理所有环境变量和配置项

注意：
- 所有敏感信息必须在 .env 文件中配置
- 本文件只负责从环境变量读取配置，不包含任何硬编码的敏感信息
"""
import os
from dotenv import load_dotenv
import logging

# 加载 .env 文件（确保在任何配置读取之前执行）
load_dotenv()

# ==================== JWT 认证配置 ====================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "未找到 SECRET_KEY 环境变量！\n"
        "请在 .env 文件中配置 JWT 密钥，例如：\n"
        "SECRET_KEY=your-secret-key-here"
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3600"))

# ==================== AI 配置 ====================
# 注意：AI 功能是可选的，未配置 API Key 不影响系统启动
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
AI_API_URL = os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-v4-flash")
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "15"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.1"))

if not DEEPSEEK_API_KEY:
    logging.warning("⚠️  未配置 DEEPSEEK_API_KEY，AI 智能助手功能将不可用")
    logging.warning("   如需使用 AI 功能，请在 .env 文件中配置 DEEPSEEK_API_KEY")


#==================== 数据库配置 ====================
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# 检查缺失的配置项
missing_db_configs = []
if not MYSQL_HOST:
    missing_db_configs.append("MYSQL_HOST")
if not MYSQL_USER:
    missing_db_configs.append("MYSQL_USER")
if not MYSQL_PASSWORD:
    missing_db_configs.append("MYSQL_PASSWORD")
if not MYSQL_DB:
    missing_db_configs.append("MYSQL_DB")

if missing_db_configs:
    raise ValueError(
        f"❌ 缺少数据库配置：{', '.join(missing_db_configs)}\n"
        "请在 .env 文件中配置：\n"
        "MYSQL_HOST=mysql      # Docker用mysql，本地用localhost\n"
        "MYSQL_PORT=3306\n"
        "MYSQL_USER=root\n"
        "MYSQL_PASSWORD=你的密码\n"
        "MYSQL_DB=door_access_system"
    )

# 自动拼接 DATABASE_URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# ==================== Redis 配置 ====================
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

# ==================== CORS 配置 ====================
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# ==================== 管理员初始化配置 ====================
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
AUTO_CREATE_ADMIN = os.getenv("AUTO_CREATE_ADMIN", "true").lower() == "true"