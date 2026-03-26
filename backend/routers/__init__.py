# backend/routers/__init__.py
from .clients import router as clients_router
from .tasks import router as tasks_router
from .alerts import router as alerts_router

__all__ = ["clients_router", "tasks_router", "alerts_router"]