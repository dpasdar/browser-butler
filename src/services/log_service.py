"""Log management service."""
import json
from datetime import datetime

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models import TaskLog, Task
from src.schemas.log import LogStatus


class LogService:
    """Service for task log operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def create(
        self,
        task_id: str,
        status: LogStatus = LogStatus.RUNNING,
    ) -> TaskLog:
        """Create a new log entry."""
        log = TaskLog(
            task_id=task_id,
            status=status.value,
            started_at=datetime.utcnow().isoformat(),
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def update(
        self,
        log_id: str,
        status: LogStatus | None = None,
        result_summary: str | None = None,
        error_message: str | None = None,
        agent_steps: list[dict] | None = None,
    ) -> TaskLog | None:
        """Update a log entry."""
        result = await self.db.execute(select(TaskLog).where(TaskLog.id == log_id))
        log = result.scalar_one_or_none()

        if not log:
            return None

        if status is not None:
            log.status = status.value
            if status != LogStatus.RUNNING:
                log.completed_at = datetime.utcnow().isoformat()
                if log.started_at:
                    started = datetime.fromisoformat(log.started_at)
                    completed = datetime.fromisoformat(log.completed_at)
                    log.duration_seconds = (completed - started).total_seconds()

        if result_summary is not None:
            log.result_summary = result_summary
        if error_message is not None:
            log.error_message = error_message
        if agent_steps is not None:
            log.agent_steps = json.dumps(agent_steps)

        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_by_id(self, log_id: str) -> TaskLog | None:
        """Get a log by ID."""
        result = await self.db.execute(
            select(TaskLog).options(joinedload(TaskLog.task)).where(TaskLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def get_by_task(
        self, task_id: str, limit: int = 50, offset: int = 0
    ) -> list[TaskLog]:
        """Get logs for a specific task."""
        result = await self.db.execute(
            select(TaskLog)
            .where(TaskLog.task_id == task_id)
            .order_by(desc(TaskLog.started_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_all(
        self,
        task_id: str | None = None,
        status: LogStatus | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> tuple[list[TaskLog], int]:
        """Get all logs with optional filters."""
        query = select(TaskLog).options(joinedload(TaskLog.task))
        count_query = select(func.count(TaskLog.id))

        if task_id:
            query = query.where(TaskLog.task_id == task_id)
            count_query = count_query.where(TaskLog.task_id == task_id)
        if status:
            query = query.where(TaskLog.status == status.value)
            count_query = count_query.where(TaskLog.status == status.value)

        query = query.order_by(desc(TaskLog.started_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        return logs, total

    async def get_running_for_task(self, task_id: str) -> TaskLog | None:
        """Get a running log for a task if it exists."""
        result = await self.db.execute(
            select(TaskLog)
            .where(TaskLog.task_id == task_id, TaskLog.status == LogStatus.RUNNING.value)
            .order_by(desc(TaskLog.started_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
