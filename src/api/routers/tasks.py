"""Task CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.services.task_service import TaskService
from src.services.scheduler_service import scheduler_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(db: AsyncSession = Depends(get_db)) -> TaskListResponse:
    """List all tasks."""
    service = TaskService(db)
    tasks = await service.get_all()
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=len(tasks),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new task."""
    service = TaskService(db)
    task = await service.create(task_data)
    await db.commit()

    # Schedule the task
    await scheduler_service.schedule_task(task)

    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Get a task by ID."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a task."""
    service = TaskService(db)
    task = await service.update(task_id, task_data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await db.commit()

    # Reschedule the task
    await scheduler_service.schedule_task(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a task."""
    service = TaskService(db)

    # Unschedule first
    await scheduler_service.unschedule_task(task_id)

    success = await service.delete(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await db.commit()


@router.post("/{task_id}/run", response_model=dict)
async def run_task_now(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Trigger immediate execution of a task."""
    service = TaskService(db)
    task = await service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    result = await scheduler_service.run_now(task_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is already running",
        )

    return {"message": "Task execution started", "task_id": task_id}


@router.post("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Toggle task enabled status."""
    service = TaskService(db)
    task = await service.toggle_enabled(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await db.commit()

    # Update scheduler
    if task.is_enabled:
        await scheduler_service.schedule_task(task)
    else:
        await scheduler_service.unschedule_task(task_id)

    return TaskResponse.model_validate(task)


@router.post("/{task_id}/duplicate", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Duplicate a task."""
    service = TaskService(db)
    original = await service.get_by_id(task_id)

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Create duplicate with modified name
    duplicate_data = TaskCreate(
        name=f"{original.name} (DUPLICATE)",
        description=original.description,
        cron_expression=original.cron_expression,
        timezone=original.timezone,
        timeout_seconds=original.timeout_seconds,
        headless=original.headless,
        start_url=original.start_url,
        telegram_enabled=original.telegram_enabled,
        telegram_chat_id=original.telegram_chat_id,
        notify_on_success=original.notify_on_success,
        notify_on_failure=original.notify_on_failure,
    )

    new_task = await service.create(duplicate_data)
    await db.commit()

    # Schedule if enabled and has cron
    if new_task.is_enabled and new_task.cron_expression:
        await scheduler_service.schedule_task(new_task)

    return TaskResponse.model_validate(new_task)
