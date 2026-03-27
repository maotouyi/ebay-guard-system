# backend/models/schema.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from core.sites import EbaySite  # 新增导入


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    wechat_webhook = Column(String(255), nullable=True)
    bark_url = Column(String(255), nullable=True)
    expire_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))

    # 监控目标
    item_id = Column(String(20), nullable=False, index=True)
    monitor_type = Column(String(20), default="price")

    # 规则阈值
    target_keyword = Column(String(100), nullable=True)
    ebay_site = Column(String(10), default=EbaySite.US.value, nullable=False)  # 新增
    location_code = Column(String(20), default="90001", nullable=False)       # 改名 + 更长

    price_threshold = Column(Float, nullable=True)
    rank_threshold = Column(Integer, nullable=True)

    # 调度配置
    check_interval = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    last_check_time = Column(DateTime, nullable=True)

    owner = relationship("Client", back_populates="tasks")
    logs = relationship("AlertLog", back_populates="task", cascade="all, delete-orphan")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))

    alert_type = Column(String(20), nullable=False)
    message = Column(String(500), nullable=False)
    is_pushed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="logs")