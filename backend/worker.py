# backend/worker.py
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from core.database import SessionLocal
from models.schema import Task, AlertLog
from scraper.engine_item import fetch_item_details
from core.config import settings
from core.alerter import trigger_alert

# 初始化调度器
scheduler = BlockingScheduler()


def job_monitor_ebay_items():
    print(f"\n[🕒 {datetime.now().strftime('%H:%M:%S')}] ⚙️ 调度器苏醒，开始轮询监控任务...")

    # 1. 连接数据库，拿任务
    db = SessionLocal()
    try:
        # 找出所有状态为 active 的任务
        active_tasks = db.query(Task).filter(Task.is_active == True).all()

        if not active_tasks:
            print("[-] 当前无活跃监控任务，继续休眠。")
            return

        for task in active_tasks:
            # 2. 调用主炮抓取
            print(f"[*] 执行任务 ID:{task.id} -> 监控 Item: {task.item_id}")
            result = fetch_item_details(
                item_id=task.item_id,
                proxy_url=settings.PROXY_URL,
                target_zipcode=settings.TARGET_ZIPCODE
            )

            # 更新最后检查时间
            task.last_check_time = datetime.utcnow()

            # 3. 核心业务逻辑：战果判定！
            if not result:
                continue

            if result['status'] == 'offline':
                alert_msg = f"Listing 已下架或被平台封杀！"
                print(f"[🚨 危险] Item {task.item_id} {alert_msg}")
                # 调用高级报警器 (传入 db session, task 实例, 报警类型, 提示信息)
                trigger_alert(db, task, alert_type="offline", message=alert_msg)

            elif result['price'] > 0 and result['price'] < task.price_threshold:
                alert_msg = f"跌破防守线！当前价: **${result['price']}** (设定阈值: ${task.price_threshold})"
                print(f"[🚨 危险] Item {task.item_id} {alert_msg}")
                # 调用高级报警器
                trigger_alert(db, task, alert_type="price_drop", message=alert_msg)
            else:
                print(f"[+] 🛡️ Item {task.item_id} 价格正常 (${result['price']})，安全防线稳固。")

        # 提交数据库更改
        db.commit()

    except Exception as e:
        print(f"[-] 调度器发生致命错误: {e}")
    finally:
        db.close()


# 设定每 3 分钟执行一次轮询任务
scheduler.add_job(job_monitor_ebay_items, 'interval', minutes=3)

if __name__ == "__main__":
    print("🦅 eBay Sleep Guard Worker 启动！")
    print("按 Ctrl+C 退出...")
    # 为了测试方便，启动时立刻执行一次，不用干等3分钟
    job_monitor_ebay_items()
    scheduler.start()