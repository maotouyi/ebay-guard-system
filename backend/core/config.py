# backend/core/config.py
import os
from dotenv import load_dotenv

# 找到 backend 目录的绝对路径，并加载 .env 文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings:
    """
    全局配置字典 (单例模式)
    所有模块通过 from backend.core.config import settings 引入
    """
    # 代理池
    PROXY_URL = os.getenv("PROXY_URL", None)

    # 默认邮编
    TARGET_ZIPCODE = os.getenv("TARGET_ZIPCODE", "90001")

    # 报警配置
    DEFAULT_WECHAT_WEBHOOK = os.getenv("DEFAULT_WECHAT_WEBHOOK", "")
    DEFAULT_BARK_URL = os.getenv("DEFAULT_BARK_URL", "")

    # 数据库路径处理
    db_env_path = os.getenv("DB_PATH", "")
    if db_env_path:
        DB_PATH = db_env_path
    else:
        # 默认放在 backend/data/guard.db
        DATA_DIR = os.path.join(BASE_DIR, "data")
        os.makedirs(DATA_DIR, exist_ok=True)
        DB_PATH = os.path.join(DATA_DIR, "guard.db")

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"


# 实例化，供外部直接调用
settings = Settings()

# 启动时打印一下配置状态，防止你找瞎了眼
print(
    f"⚙️  系统配置已加载 | 代理状态: {'已挂载' if settings.PROXY_URL else '直连模式'} | 目标邮编: {settings.TARGET_ZIPCODE}")