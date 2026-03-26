# backend/worker.py
import time
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.schema import Task, AlertLog
from scraper.engine_item import fetch_item_details
from scraper.engine_search import fetch_ebay_search_rank
from core.config import settings
from core.alerter import trigger_alert

# 初始化调度器（全局轮询模式，符合 README 独立 worker 设计）
scheduler = BlockingScheduler()


def job_monitor_ebay_items():
    """主调度任务：每 3 分钟唤醒一次，检查所有活跃任务"""
    print(f"\n[🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚙️ eBay Sleep Guard Worker 苏醒，开始轮询...")

    db: Session = SessionLocal()
    try:
        active_tasks = db.query(Task).filter(Task.is_active == True).all()

        if not active_tasks:
            print("[-] 当前无活跃任务，休眠中...")
            return

        for task in active_tasks:
            # ================== 1. 尊重任务自定义频率 ==================
            if task.last_check_time:
                time_since_last = (datetime.utcnow() - task.last_check_time).total_seconds() / 60
                if time_since_last < task.check_interval:
                    print(f"[⏭️ 跳过] Task {task.id} (Item {task.item_id}) 尚未到检查时间（间隔 {task.check_interval} 分钟）")
                    continue

            # ================== 2. 随机防风控延迟 ==================
            delay = random.uniform(1.0, 4.0)
            print(f"[*] Task {task.id} | Item {task.item_id} | 类型: {task.monitor_type} | 邮编: {task.target_zipcode} | 延迟 {delay:.1f}s")
            time.sleep(delay)

            # ================== 3. 根据 monitor_type 分流抓取 ==================
            result = None
            alert_type = None
            alert_msg = None

            if task.monitor_type == "price":
                # 使用全新修复的 engine_item.py
                result = fetch_item_details(
                    item_id=task.item_id,
                    proxy_url=settings.PROXY_URL,
                    target_zipcode=task.target_zipcode
                )

                if not result:
                    continue

                if result.get("status") == "offline":
                    alert_type = "offline"
                    alert_msg = f"Listing 已下架或被平台封杀！"
                elif result.get("price", 0) > 0 and task.price_threshold and result["price"] < task.price_threshold:
                    alert_type = "price_drop"
                    alert_msg = f"跌破防守线！当前价: **${result['price']:.2f}**（阈值: ${task.price_threshold}）"

            elif task.monitor_type == "rank":
                # 使用 engine_search.py（支持关键词 + 目标 Item 排名）
                if not task.target_keyword:
                    print(f"[-] ⚠️ Rank 任务 {task.id} 缺少 target_keyword，跳过")
                    continue

                result = fetch_ebay_search_rank(
                    keyword=task.target_keyword,
                    target_item_id=task.item_id,
                    proxy_url=settings.PROXY_URL,
                    target_zipcode=task.target_zipcode
                )

                if not result:
                    continue

                rank = result.get("target_rank", -1)
                if rank == -1:
                    alert_type = "rank_not_found"
                    alert_msg = f"关键词「{task.target_keyword}」搜索中未找到 Item {task.item_id}！可能已下架或排名极低"
                elif rank > 0:
                    print(f"[📊 排名监控] Item {task.item_id} 当前自然排名第 {rank} 名（关键词：{task.target_keyword}）")
                    # 当前 schema 无 rank_threshold，可后续扩展；暂仅记录不报警
                # 其他情况（如排名正常）不触发报警

            else:
                print(f"[-] 未知 monitor_type: {task.monitor_type}，跳过")
                continue

            # ================== 4. 更新最后检查时间 ==================
            task.last_check_time = datetime.utcnow()

            # ================== 5. 触发报警（仅当有 alert_msg 时）==================
            if alert_type and alert_msg:
                print(f"[🚨 报警] Task {task.id} | {alert_type} | {alert_msg}")
                trigger_alert(
                    db=db,
                    task=task,
                    alert_type=alert_type,
                    message=alert_msg
                )
            else:
                print(f"[✅ 安全] Item {task.item_id} 状态正常")

        # ================== 6. 统一提交 ==================
        db.commit()
        print(f"[+] 本轮轮询完成，共处理 {len(active_tasks)} 个任务")

    except Exception as e:
        print(f"[-] ❌ Worker 发生致命错误: {e}")
    finally:
        db.close()


# ================== 调度配置 ==================
# 全局轮询间隔（推荐 3 分钟，符合 README 轻量设计）
scheduler.add_job(job_monitor_ebay_items, 'interval', minutes=3, id='main_monitor')

if __name__ == "__main__":
    print("🦅 eBay Sleep Guard Worker 已启动！（按 Ctrl+C 退出）")
    # 启动时立即执行一次，方便测试
    job_monitor_ebay_items()
    scheduler.start()