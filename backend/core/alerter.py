# backend/core/alerter.py
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from curl_cffi import requests
from models.schema import AlertLog, Task
from core.config import settings


# ====================== 企微推送已完全注释掉 ======================
# def send_wechat_alert(...):
#     ...（全部注释）
# def trigger_alert 中原来的企微逻辑也已注释
# ==================================================================


def send_bark_alert(bark_url: str, title: str, body: str):
    """Bark 推送函数（与 eBay 抓取统一使用 curl_cffi + chrome120 伪装）"""
    if not bark_url:
        print("[-] ⚠️ 未配置 Bark URL，跳过推送")
        return False

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {
        "title": title,
        "body": body,
        "sound": "alarm",  # 可选：响铃
        "icon": "https://i.imgur.com/8z5vJ0K.png",  # 可选：小图标（eBay 风格）
        "group": "eBay鹰眼"  # 可选：分组
    }

    proxies = {"http": None, "https": None}

    try:
        session = requests.Session(impersonate="chrome120")
        resp = session.post(
            bark_url.rstrip('/'),  # 防止多一个 /
            json=payload,
            headers=headers,
            proxies=proxies,
            timeout=15
        )

        print(f"[*] Bark 响应状态码: {resp.status_code}")

        try:
            resp_data = resp.json()
            if resp_data.get("code") == 200:
                print("[+] 📲 Bark 推送成功！")
                return True
            else:
                print(f"[-] ❌ Bark 官方拒绝！ code: {resp_data.get('code')} | message: {resp_data.get('message')}")
                return False
        except json.JSONDecodeError:
            print(f"[-] ❌ 非 JSON 响应: {resp.text[:300]}")
            return resp.status_code == 200

    except Exception as e:
        print(f"[-] 💥 Bark 请求崩溃: {e}")
        return False


def trigger_alert(db: Session, task: Task, alert_type: str, message: str, cooldown_hours: int = 4):
    """高级拦截器：带 4 小时冷却 + Bark 推送"""

    # 1. 冷却检查（保持不变）
    cutoff_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
    recent_alert = db.query(AlertLog).filter(
        AlertLog.task_id == task.id,
        AlertLog.alert_type == alert_type,
        AlertLog.is_pushed == True,
        AlertLog.created_at >= cutoff_time
    ).first()
    if recent_alert:
        print(f"[*] 🛡️ [冷却拦截] Item {task.item_id} 的 '{alert_type}' 报警处于冷却期")
        return False

    # 2. 获取 Bark URL（优先用户私有 → 系统默认）
    bark_url = getattr(task.owner, 'bark_url', None) if task.owner else None
    bark_url = bark_url or settings.DEFAULT_BARK_URL  # ← 你后面在 settings 加这个

    # 3. 组装 Bark 消息
    title = "🚨 eBay 鹰眼监控报警"
    body = f"""监控目标: {task.item_id}
异常类型: {alert_type}
详细情况: {message}
发生时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
链接: https://www.ebay.com/itm/{task.item_id}"""

    # 4. 执行 Bark 推送
    push_success = False
    if bark_url:
        print(f"[*] 正在推送至 Bark: {bark_url[:60]}...")
        push_success = send_bark_alert(bark_url=bark_url, title=title, body=body)
    else:
        print("[-] ⚠️ 未找到 Bark URL，无法推送")

    # 5. 记录日志（保持和原来一样）
    new_log = AlertLog(
        task_id=task.id,
        alert_type=alert_type,
        message=message,
        is_pushed=push_success
    )
    db.add(new_log)
    db.commit()

    return push_success