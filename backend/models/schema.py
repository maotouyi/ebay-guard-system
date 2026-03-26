# backend/models/schema.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)                    # 客户名称 (如: 张总-汽配)
    wechat_webhook = Column(String(255), nullable=True)          # 企微机器人推送地址（可选）
    bark_url = Column(String(255), nullable=True)                # Bark推送地址（推荐，alerter优先使用）
    expire_date = Column(DateTime, nullable=False)               # 订阅到期时间，到期自动停抓
    is_active = Column(Boolean, default=True)                    # 软删除标记
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联任务
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))

    # 监控目标
    item_id = Column(String(20), nullable=False, index=True)
    monitor_type = Column(String(20), default="price")           # price(价格/跟卖), rank(排名/流量)

    # 规则阈值
    target_keyword = Column(String(100), nullable=True)          # 如果查排名，必须绑定关键词
    target_zipcode = Column(String(10), default="90001")         # 目标邮编（ZipCode注入）
    price_threshold = Column(Float, nullable=True)               # 跌破此价格报警（USD）
    rank_threshold = Column(Integer, nullable=True)              # 排名变差报警（例如 >10 即报警，数值越小越好）

    # 调度配置
    check_interval = Column(Integer, default=30)                 # 抓取频率(分钟)，worker已支持
    is_active = Column(Boolean, default=True)                    # 任务开关
    last_check_time = Column(DateTime, nullable=True)            # 上次执行时间（worker自动更新）

    owner = relationship("Client", back_populates="tasks")
    logs = relationship("AlertLog", back_populates="task", cascade="all, delete-orphan")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))

    alert_type = Column(String(20), nullable=False)              # 报警类型: price_drop, offline, rank_drop, error
    message = Column(String(500), nullable=False)                # 具体报警内容（支持Markdown）
    is_pushed = Column(Boolean, default=False)                   # 是否已经推送到客户端 (用于冷却判定)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="logs")