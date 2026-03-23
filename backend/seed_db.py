# backend/seed_db.py
from datetime import datetime, timedelta
from core.database import SessionLocal
from models.schema import Client


def seed_initial_data():
    db = SessionLocal()
    try:
        # 检查是不是已经有数据了
        existing_client = db.query(Client).filter(Client.id == 1).first()
        if existing_client:
            print("[*] 数据库里已经有客户了，不用重复添加。")
            return

        # 伪造一个能用 10 年的 VIP 客户
        dummy_client = Client(
            name="头号金主-你自己",
            wechat_webhook="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            expire_date=datetime.utcnow() + timedelta(days=3650),  # 10年后到期
            is_active=True
        )

        db.add(dummy_client)
        db.commit()
        print("[+] ✅ 成功！'头号金主' 已就位，Client ID 为: 1")

    except Exception as e:
        print(f"[-] 插入失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_initial_data()