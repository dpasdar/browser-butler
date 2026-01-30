"""Task CRUD operations service."""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Task
from src.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service for task CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def get_all(self) -> list[Task]:
        """Get all tasks."""
        result = await self.db.execute(select(Task).order_by(Task.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_enabled(self) -> list[Task]:
        """Get all enabled tasks."""
        result = await self.db.execute(
            select(Task).where(Task.is_enabled == True).order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(**task_data.model_dump())
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update(self, task_id: str, task_data: TaskUpdate) -> Task | None:
        """Update a task."""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: str) -> bool:
        """Delete a task."""
        task = await self.get_by_id(task_id)
        if not task:
            return False

        await self.db.delete(task)
        await self.db.flush()
        return True

    async def toggle_enabled(self, task_id: str) -> Task | None:
        """Toggle task enabled status."""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        task.is_enabled = not task.is_enabled
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_run_times(
        self, task_id: str, last_run_at: str | None = None, next_run_at: str | None = None
    ) -> Task | None:
        """Update task run times."""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        if last_run_at is not None:
            task.last_run_at = last_run_at
        if next_run_at is not None:
            task.next_run_at = next_run_at

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def count(self) -> int:
        """Get total task count."""
        result = await self.db.execute(select(func.count(Task.id)))
        return result.scalar_one()
