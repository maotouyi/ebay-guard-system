# backend/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from core.database import get_db
from models.schema import Task
from core.sites import EbaySite  # 新增导入

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


# ================== 支持前端 camelCase ==================
class TaskCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    client_id: int = Field(alias="clientId")
    item_id: str = Field(alias="itemId")
    monitor_type: str = Field(default="price", alias="monitorType")
    target_keyword: Optional[str] = Field(default=None, alias="targetKeyword")

    # === 多国家优化核心字段 ===
    ebay_site: EbaySite = Field(default=EbaySite.US, alias="ebaySite")  # 新增
    location_code: str = Field(default="90001", alias="locationCode")  # 改名

    price_threshold: Optional[float] = Field(default=None, alias="priceThreshold")
    rank_threshold: Optional[int] = Field(default=None, alias="rankThreshold")
    check_interval: int = Field(default=30, alias="checkInterval")


class TaskRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    client_id: int = Field(alias="clientId")
    item_id: str = Field(alias="itemId")
    monitor_type: str = Field(alias="monitorType")
    target_keyword: Optional[str] = Field(alias="targetKeyword")

    ebay_site: str = Field(alias="ebaySite")  # 新增
    location_code: str = Field(alias="locationCode")  # 改名

    price_threshold: Optional[float] = Field(alias="priceThreshold")
    rank_threshold: Optional[int] = Field(alias="rankThreshold")
    check_interval: int = Field(alias="checkInterval")
    is_active: bool


@router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    print(f"[DEBUG] 收到前端创建任务请求 → {task.model_dump(by_alias=True)}")
    # 自动转 snake_case 存库
    db_task = Task(**task.model_dump(by_alias=False))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    print(f"[+] 新任务创建成功 → Task ID: {db_task.id} | Site: {db_task.ebay_site} | Location: {db_task.location_code}")
    return db_task


@router.get("/", response_model=List[TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    print(f"[DEBUG] 当前数据库中共有 {len(tasks)} 个任务")
    return tasks


@router.put("/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_active = not task.is_active
    db.commit()
    db.refresh(task)
    return {"id": task.id, "is_active": task.is_active}