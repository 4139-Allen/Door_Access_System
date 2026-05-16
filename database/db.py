
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DATABASE_URL

if not DATABASE_URL:
    raise ValueError(
        "未找到 DATABASE_URL 环境变量！\n"
        "请在 .env 文件中配置数据库连接，例如：\n"
        "DATABASE_URL=mysql+pymysql://root:你的密码@localhost/door_access_system"
    )

#连接池配置
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 最大溢出连接数
    pool_recycle=3600,      # 连接回收时间（秒）
    pool_pre_ping=True      # 连接前检查是否有效
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()   # 创建基类

# 依赖注入（给FastAPI用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

