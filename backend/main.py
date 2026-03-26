# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.database import engine
from models.schema import Base
from routers import clients_router, tasks_router, alerts_router
from core.config import settings

app = FastAPI(
    title="eBay Sleep Guard 后台管理系统",
    description="一人管控后台 | 价格防卫 + 排名监控 | Bark推送 | 模块化路由",
    version="1.5",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载所有路由
app.include_router(clients_router)
app.include_router(tasks_router)
app.include_router(alerts_router)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("🚀 FastAPI 已启动 | 路由已全部拆分 | Swagger: http://127.0.0.1:8000/docs")

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)