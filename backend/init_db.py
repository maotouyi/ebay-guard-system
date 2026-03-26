# backend/init_db.py
from core.database import engine, Base
from models.schema import Client, Task, AlertLog  # 确保最新 schema 被加载

def init_database():
    """初始化/重建数据库（全新表结构）"""
    print("🗑️ 正在删除旧表结构并重建...")
    Base.metadata.drop_all(bind=engine)   # 安全重建
    Base.metadata.create_all(bind=engine)
    print("🎉 数据库表结构初始化完成！")
    print("当前表结构：clients、tasks、alert_logs（已包含 bark_url 和 rank_threshold）")

if __name__ == "__main__":
    init_database()