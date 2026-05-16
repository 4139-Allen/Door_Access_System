from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import routers
from core.config import ALLOWED_ORIGINS
from database.db import init_database
from fastapi import Request
from utils.response import error
# 导入封装好的日志类
from utils.logger import AppLogger
from contextlib import asynccontextmanager
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ===== 启动时执行 =====
    app_logger = AppLogger.get_logger()
    app_logger.info("=" * 50)
    app_logger.info("🚀 门禁管理系统正在启动...")
    app_logger.info("=" * 50)

    # 1. 初始化数据库（建库 + 建表）
    try:
        # 如需重置数据库，取消下一行注释并重启（⚠️ 会清空所有数据）
        # drop_all_tables()
        init_database()
    except Exception as e:
        app_logger.error(f"⚠️ 数据库初始化失败，服务将无法正常运行: {e}")

    # 2. 初始化管理员账户
    try:
        from database.admin import init_admin
        init_admin()
    except Exception as e:
        app_logger.error(f"⚠️ 管理员初始化失败: {e}")

    app_logger.info("=" * 50)
    app_logger.info("✅ 门禁管理系统服务启动成功 🚀")
    app_logger.info("📍 服务地址: http://127.0.0.1:8000")
    app_logger.info("📖 文档地址: http://127.0.0.1:8000/docs")
    app_logger.info("=" * 50)

    yield  # 应用运行期间

    # ===== 关闭时执行 =====
    app_logger.info("=" * 50)
    app_logger.info("🛑 门禁管理系统正在关闭...")
    app_logger.info("=" * 50)



app = FastAPI(title="门禁管理系统", version="1.0", lifespan=lifespan)  #  传入 lifespan

# # 删除所有表
# Base.metadata.drop_all(bind=engine)

# CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有 HTTP 请求"""
    start_time = time.time()
    
    # 执行请求
    response = await call_next(request)
    
    # 计算耗时
    duration = time.time() - start_time
    
    # 获取客户端 IP
    client_host = request.client.host if request.client else "unknown"
    
    # 记录日志（跳过健康检查和静态文件）
    if not request.url.path.startswith("/health"):
        logger = AppLogger.get_logger()
        logger.info(
            f"📊 {request.method} {request.url.path} | "
            f"状态: {response.status_code} | "
            f"耗时: {duration:.3f}s | "
            f"IP: {client_host}"
        )
    
    return response

# 路由
app.include_router(routers)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，捕获所有未处理的异常"""
    logger = AppLogger.get_logger()
    logger.error(
        f"💥 未处理的异常 | "
        f"[{request.method} {request.url}] | "
        f"错误: {str(exc)}",
        exc_info=True  # 记录完整堆栈
    )

    return error(msg="服务器内部错误", code=500)


# 健康检查端点
@app.get("/health", summary="健康检查")
def health_check():
    return {"status": "healthy", "service": "door_access_system"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
