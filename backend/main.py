# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uvicorn
from sqlalchemy import desc, func
from models.schema import AlertLog # 确保引入了日志表

# 引入我们之前写的数据库和模型
from core.database import get_db, engine, Base
from models.schema import Task, Client

# 创建 FastAPI 实例
app = FastAPI(title="eBay Sleep Guard API", version="1.5")

# --- Pydantic 数据验证模型 (用于接收前端传来的 JSON) ---
class TaskCreate(BaseModel):
    client_id: int
    item_id: str
    monitor_type: str = "price"
    price_threshold: float

# --- API 路由 ---

@app.get("/")
def read_root():
    return {"message": "🦅 eBay Sleep Guard API is running!"}

@app.post("/api/tasks/", summary="添加监控任务")
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    # 检查客户是否存在 (为了测试，你可以先去数据库手动加个 client_id=1 的客户，或者忽略外键)
    new_task = Task(
        client_id=task_in.client_id,
        item_id=task_in.item_id,
        monitor_type=task_in.monitor_type,
        price_threshold=task_in.price_threshold,
        check_interval=5 # 默认5分钟抓一次
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"status": "success", "task_id": new_task.id, "msg": f"Item {task_in.item_id} 已加入监控列队"}

@app.get("/api/tasks/", summary="获取所有活跃任务")
def get_active_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.is_active == True).all()
    return tasks

if __name__ == "__main__":
    # 启动命令
    print("🚀 启动 FastAPI 中枢神经...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# ==========================================
# 📊 V1.5 主控台前端支撑 API
# ==========================================

@app.get("/api/stats/", summary="获取主控台大盘数据 (用于装逼大屏)")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取系统整体运行状态"""
    # 统计活跃任务数
    active_tasks = db.query(Task).filter(Task.is_active == True).count()
    # 统计总战果数
    total_alerts = db.query(AlertLog).count()
    # 统计今日战果 (巧妙利用 SQLite 的 date 函数)
    today_alerts = db.query(AlertLog).filter(func.date(AlertLog.created_at) == func.date('now')).count()

    return {
        "active_tasks": active_tasks,
        "total_alerts": total_alerts,
        "today_alerts": today_alerts
    }


@app.get("/api/logs/", summary="获取最新战果日志 (用于滚动终端)")
def get_recent_logs(limit: int = 50, db: Session = Depends(get_db)):
    """按时间倒序获取最近的报警日志"""
    # 联表查询，按时间倒序排，最多拿 50 条防止前端卡顿
    logs = db.query(AlertLog).order_by(desc(AlertLog.created_at)).limit(limit).all()

    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "item_id": log.task.item_id if log.task else "未知",
            "alert_type": log.alert_type,
            "message": log.message,
            "is_pushed": log.is_pushed,
            "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return result


@app.put("/api/tasks/{task_id}/stop", summary="停止监控任务 (软删除)")
def stop_task(task_id: int, db: Session = Depends(get_db)):
    """客户不交钱了？一键停掉他的监控"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="未找到该任务")

    task.is_active = False  # 软删除，保留历史记录
    db.commit()
    return {"status": "success", "msg": f"任务 ID:{task_id} 已停止监控"}


@app.get("/api/clients/", summary="获取私域客户列表")
def get_clients(db: Session = Depends(get_db)):
    """查看你的金主名单"""
    clients = db.query(Client).filter(Client.is_active == True).all()
    return clients