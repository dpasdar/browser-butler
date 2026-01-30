"""System status and health endpoints."""
from fastapi import APIRouter

from src.services.scheduler_service import scheduler_service
from src.services.event_manager import event_manager
from src.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/status")
async def system_status() -> dict:
    """Get system status including scheduler and running tasks."""
    jobs = scheduler_service.get_all_jobs()
    running_tasks = scheduler_service.get_running_tasks()

    return {
        "scheduler": {
            "running": scheduler_service.scheduler.running,
            "scheduled_jobs": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                }
                for job in jobs
            ],
        },
        "running_tasks": running_tasks,
        "sse_subscribers": event_manager.subscriber_count,
        "config": {
            "telegram_configured": bool(settings.telegram_bot_token),
            "openai_configured": bool(settings.openai_api_key),
        },
    }
