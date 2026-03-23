# init_db.py
from core.database import engine, Base
from models.schema import Client, Task, AlertLog

print("🚀 开始初始化数据库表结构...")
Base.metadata.create_all(bind=engine)
print("✅ 数据库建表完成！请检查 data/guard.db 文件是否生成。")