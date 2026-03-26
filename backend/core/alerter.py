# backend/core/alerter.py
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from curl_cffi import requests

from models.schema import AlertLog, Task
from core.config import settings


def send_bark_alert(bark_url: str, title: str, body: str) -> bool:
    """Bark 推送函数（统一使用 curl_cffi + chrome120 伪装，防封）"""
    if not bark_url:
        print("[-] 未配置 Bark URL，跳过推送")
        return False

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {
        "title": title,
        "body": body,
        "sound": "alarm",           # 响铃提醒
        "icon": "https://i.imgur.com/8z5vJ0K.png",   # eBay风格小图标
        "group": "eBay鹰眼监控"     # Bark分组
    }

    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.post(
            bark_url.rstrip('/'),
            json=payload,
            headers=headers,
            proxies={"http": None, "https": None},
            timeout=15
        )

        print(f"[*] Bark 推送响应状态码: {resp.status_code}")

        try:
            resp_data = resp.json()
            if resp_data.get("code") == 200:
                print("[+] ✅ Bark 推送成功！")
                return True
            else:
                print(f"[-] Bark 官方拒绝！ code: {resp_data.get('code')} | msg: {resp_data.get('message')}")
                return False
        except json.JSONDecodeError:
            print(f"[-] 非JSON响应: {resp.text[:300]}")
            return resp.status_code == 200

    except Exception as e:
        print(f"[-] ❌ Bark 请求异常: {e}")
        return False


def trigger_alert(
    db: Session,
    task: Task,
    alert_type: str,
    message: str,
    cooldown_hours: int = 4
) -> bool:
    """
    高级报警拦截器（核心逻辑）
    - 4小时同类型冷却
    - 优先 Client.bark_url（私有）→ settings.DEFAULT_BARK_URL
    - 自动记录 AlertLog
    """
    # 1. 冷却检查（防止刷屏）
    cutoff_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
    recent_alert = db.query(AlertLog).filter(
        AlertLog.task_id == task.id,
        AlertLog.alert_type == alert_type,
        AlertLog.is_pushed == True,
        AlertLog.created_at >= cutoff_time
    ).first()

    if recent_alert:
        print(f"[*] [冷却拦截] Item {task.item_id} 的 '{alert_type}' 已在冷却期内，跳过推送")
        return False

    # 2. 获取 Bark URL（新 schema 已支持）
    bark_url = getattr(task.owner, 'bark_url', None) if hasattr(task, 'owner') and task.owner else None
    bark_url = bark_url or settings.DEFAULT_BARK_URL

    # 3. 组装消息（Markdown友好）
    title = "🚨 eBay 鹰眼监控报警"
    body = f"""监控目标: **{task.item_id}**
异常类型: **{alert_type}**
详细情况: {message}
发生时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
直达链接: https://www.ebay.com/itm/{task.item_id}"""

    # 4. 执行推送
    push_success = False
    if bark_url:
        print(f"[*] 正在推送 Bark → {bark_url[:60]}...（任务 {task.id}）")
        push_success = send_bark_alert(bark_url=bark_url, title=title, body=body)
    else:
        print("[-] 未找到任何 Bark URL（Client.bark_url 和 DEFAULT_BARK_URL 均为空），无法推送")

    # 5. 记录日志（无论推送是否成功都记录）
    new_log = AlertLog(
        task_id=task.id,
        alert_type=alert_type,
        message=message,
        is_pushed=push_success
    )
    db.add(new_log)
    db.commit()

    if push_success:
        print(f"[+] 报警记录已入库 + 推送成功（Task {task.id}）")
    else:
        print(f"[⚠️] 报警记录已入库，但推送失败（Task {task.id}）")

    return push_success