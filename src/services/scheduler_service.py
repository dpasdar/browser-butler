"""APScheduler management service."""
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

from src.config import settings
from src.db import async_session
from src.db.models import Task
from src.schemas.log import LogStatus
from src.services.task_service import TaskService
from src.services.log_service import LogService
from src.services.agent_executor import agent_executor
from src.services.notification_service import notification_service

if TYPE_CHECKING:
    from src.services.event_manager import EventManager

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks."""

    def __init__(self):
        """Initialize the scheduler service."""
        self.scheduler = AsyncIOScheduler()
        self._event_manager: "EventManager | None" = None
        self._running_tasks: dict[str, str] = {}  # task_id -> log_id

    def set_event_manager(self, event_manager: "EventManager") -> None:
        """Set the event manager for SSE updates."""
        self._event_manager = event_manager

    async def start(self) -> None:
        """Start the scheduler and load all enabled tasks."""
        self.scheduler.start()
        logger.info("Scheduler started")

        # Load all enabled tasks
        async with async_session() as db:
            task_service = TaskService(db)
            tasks = await task_service.get_enabled()

            for task in tasks:
                await self.schedule_task(task)

            logger.info(f"Loaded {len(tasks)} enabled tasks")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")

    async def schedule_task(self, task: Task) -> bool:
        """Schedule or reschedule a task."""
        job_id = f"task_{task.id}"

        # Remove existing job if any
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        if not task.is_enabled:
            return False

        # Manual-only tasks (no cron expression) don't get scheduled
        if not task.cron_expression:
            return False

        try:
            # Parse cron expression
            trigger = CronTrigger.from_crontab(task.cron_expression, timezone=task.timezone)

            # Add job
            job = self.scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                id=job_id,
                args=[task.id],
                replace_existing=True,
            )

            # Update next run time
            if job.next_run_time:
                async with async_session() as db:
                    task_service = TaskService(db)
                    await task_service.update_run_times(
                        task.id, next_run_at=job.next_run_time.isoformat()
                    )
                    await db.commit()

            logger.info(f"Scheduled task {task.id} with cron '{task.cron_expression}'")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule task {task.id}: {e}")
            return False

    async def unschedule_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler."""
        job_id = f"task_{task_id}"

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Unscheduled task {task_id}")
            return True
        return False

    async def run_now(self, task_id: str) -> str | None:
        """Trigger immediate execution of a task."""
        async with async_session() as db:
            task_service = TaskService(db)
            task = await task_service.get_by_id(task_id)

            if not task:
                return None

            # Check if already running
            if task_id in self._running_tasks:
                logger.warning(f"Task {task_id} is already running")
                return None

            # Execute in background
            import asyncio
            asyncio.create_task(self._execute_task(task_id))

            return task_id

    async def _execute_task(self, task_id: str) -> None:
        """Execute a task."""
        async with async_session() as db:
            task_service = TaskService(db)
            log_service = LogService(db)

            task = await task_service.get_by_id(task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return

            # Check if already running
            if task_id in self._running_tasks:
                logger.warning(f"Task {task_id} is already running")
                return

            # Create log entry
            log = await log_service.create(task_id)
            await db.commit()

            self._running_tasks[task_id] = log.id

            # Notify SSE clients
            if self._event_manager:
                await self._event_manager.broadcast({
                    "type": "task_started",
                    "task_id": task_id,
                    "log_id": log.id,
                })

            try:
                logger.info(f"Executing task {task_id}: {task.name}")

                # Execute the agent
                status, result_summary, error_message, steps = await agent_executor.execute(task)

                # Update log
                log = await log_service.update(
                    log.id,
                    status=status,
                    result_summary=result_summary,
                    error_message=error_message,
                    agent_steps=steps,
                )
                await db.commit()

                # Update task last run time
                await task_service.update_run_times(
                    task_id, last_run_at=datetime.utcnow().isoformat()
                )

                # Get next run time
                job = self.scheduler.get_job(f"task_{task_id}")
                if job and job.next_run_time:
                    await task_service.update_run_times(
                        task_id, next_run_at=job.next_run_time.isoformat()
                    )

                await db.commit()

                # Send notification
                await self._send_notification(task, log)

                logger.info(f"Task {task_id} completed with status: {status}")

            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")

                # Update log with error
                await log_service.update(
                    log.id,
                    status=LogStatus.FAILURE,
                    error_message=str(e),
                )
                await db.commit()

                # Send failure notification
                if task.telegram_enabled and task.notify_on_failure:
                    await notification_service.notify_task_failure(
                        task.name,
                        str(e),
                        chat_id=task.telegram_chat_id,
                    )

            finally:
                self._running_tasks.pop(task_id, None)

                # Notify SSE clients
                if self._event_manager:
                    await self._event_manager.broadcast({
                        "type": "task_completed",
                        "task_id": task_id,
                        "log_id": log.id,
                        "status": log.status if log else "unknown",
                    })

    async def _send_notification(self, task: Task, log) -> None:
        """Send notification based on task result."""
        if not task.telegram_enabled:
            return

        chat_id = task.telegram_chat_id

        if log.status == LogStatus.SUCCESS.value and task.notify_on_success:
            await notification_service.notify_task_success(
                task.name,
                log.result_summary,
                log.duration_seconds,
                chat_id,
            )
        elif log.status == LogStatus.FAILURE.value and task.notify_on_failure:
            await notification_service.notify_task_failure(
                task.name,
                log.error_message,
                log.duration_seconds,
                chat_id,
            )
        elif log.status == LogStatus.TIMEOUT.value and task.notify_on_failure:
            await notification_service.notify_task_timeout(
                task.name,
                task.timeout_seconds,
                chat_id,
            )

    def get_job(self, task_id: str) -> Job | None:
        """Get a scheduled job by task ID."""
        return self.scheduler.get_job(f"task_{task_id}")

    def get_running_tasks(self) -> dict[str, str]:
        """Get currently running tasks."""
        return self._running_tasks.copy()

    def get_all_jobs(self) -> list[Job]:
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()


# Global instance
scheduler_service = SchedulerService()
