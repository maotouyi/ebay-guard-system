# backend/seed_db.py
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.schema import Client, Task
from datetime import datetime, timedelta

def seed_test_data():
    """插入测试客户 + 测试任务（一人后台手动输入风格）"""
    db: Session = SessionLocal()
    try:
        # 1. 测试客户（支持 Bark）
        client = Client(
            name="测试客户-张总",
            bark_url="https://api.day.app/your_bark_key_here",   # ← 这里改成你自己的 Bark 地址
            wechat_webhook=None,
            expire_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        print(f"[+] 测试客户创建成功 → ID: {client.id} | Name: {client.name}")

        # 2. 测试任务（Price + Rank 各一个）
        task1 = Task(
            client_id=client.id,
            item_id="123456789012",           # ← 改成你想监控的真实 eBay Item ID
            monitor_type="price",
            target_zipcode="90001",
            price_threshold=89.99,
            check_interval=15,
            is_active=True
        )
        task2 = Task(
            client_id=client.id,
            item_id="123456789012",
            monitor_type="rank",
            target_keyword="wireless earbuds",   # ← 改成真实关键词
            target_zipcode="90001",
            rank_threshold=5,                    # 排名 >5 名就报警
            check_interval=30,
            is_active=True
        )
        db.add(task1)
        db.add(task2)
        db.commit()

        print(f"[+] 测试任务创建成功 → Price任务 ID: {task1.id} | Rank任务 ID: {task2.id}")
        print("\n✅ 现在可以打开 Swagger 测试 API，或直接运行 worker.py")

    except Exception as e:
        print(f"[-] Seed 数据插入失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()