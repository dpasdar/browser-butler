"""API routers module."""
from .tasks import router as tasks_router
from .logs import router as logs_router
from .events import router as events_router
from .system import router as system_router

__all__ = ["tasks_router", "logs_router", "events_router", "system_router"]
