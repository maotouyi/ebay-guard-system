# backend/routers/alerts.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from core.database import get_db
from models.schema import AlertLog

router = APIRouter(prefix="/api/alerts", tags=["Alerts & Dashboard"])   # ← 改成 /api/alerts

class AlertLogRead(BaseModel):
    id: int
    task_id: int
    alert_type: str
    message: str
    is_pushed: bool
    created_at: datetime

@router.get("/", response_model=List[AlertLogRead])
def list_alerts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AlertLog).order_by(AlertLog.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    from models.schema import Client, Task
    total_clients = db.query(Client).count()
    active_tasks = db.query(Task).filter(Task.is_active == True).count()
    total_alerts = db.query(AlertLog).count()
    recent_alerts = db.query(AlertLog).order_by(AlertLog.created_at.desc()).limit(5).all()

    return {
        "total_clients": total_clients,
        "active_tasks": active_tasks,
        "total_alerts": total_alerts,
        "recent_alerts": [
            {"task_id": a.task_id, "type": a.alert_type, "message": a.message, "time": a.created_at}
            for a in recent_alerts
        ]
    }