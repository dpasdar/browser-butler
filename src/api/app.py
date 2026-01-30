"""FastAPI application factory."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.db import init_db
from src.services.scheduler_service import scheduler_service
from src.services.event_manager import event_manager
from src.services.notification_service import notification_service
from src.api.routers import tasks_router, logs_router, events_router, system_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting application...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Set up event manager for scheduler
    scheduler_service.set_event_manager(event_manager)

    # Start scheduler
    await scheduler_service.start()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await scheduler_service.stop()
    await notification_service.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Browser Automation API",
        description="AI-powered browser automation with scheduling and notifications",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routers
    app.include_router(tasks_router, prefix="/api")
    app.include_router(logs_router, prefix="/api")
    app.include_router(events_router, prefix="/api")
    app.include_router(system_router, prefix="/api")

    # Serve frontend static files if available
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app
