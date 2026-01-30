"""Log query endpoints."""
import json
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.schemas.log import LogResponse, LogListResponse, LogStatus
from src.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["logs"])


def _log_to_response(log, task_name: str | None = None) -> LogResponse:
    """Convert a log model to response schema."""
    agent_steps = None
    if log.agent_steps:
        try:
            agent_steps = json.loads(log.agent_steps)
        except json.JSONDecodeError:
            pass

    return LogResponse(
        id=log.id,
        task_id=log.task_id,
        task_name=task_name or (log.task.name if hasattr(log, "task") and log.task else None),
        status=LogStatus(log.status),
        started_at=log.started_at,
        completed_at=log.completed_at,
        duration_seconds=log.duration_seconds,
        result_summary=log.result_summary,
        error_message=log.error_message,
        agent_steps=agent_steps,
        created_at=log.created_at,
    )


@router.get("", response_model=LogListResponse)
async def list_logs(
    task_id: str | None = Query(default=None, description="Filter by task ID"),
    status: LogStatus | None = Query(default=None, description="Filter by status"),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=25, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> LogListResponse:
    """List all logs with optional filters."""
    service = LogService(db)
    offset = (page - 1) * per_page

    logs, total = await service.get_all(
        task_id=task_id,
        status=status,
        limit=per_page,
        offset=offset,
    )

    total_pages = ceil(total / per_page) if total > 0 else 1

    return LogListResponse(
        logs=[_log_to_response(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: str,
    db: AsyncSession = Depends(get_db),
) -> LogResponse:
    """Get a log by ID."""
    service = LogService(db)
    log = await service.get_by_id(log_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found",
        )

    return _log_to_response(log)


@router.get("/task/{task_id}", response_model=LogListResponse)
async def get_task_logs(
    task_id: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=25, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> LogListResponse:
    """Get logs for a specific task."""
    service = LogService(db)
    offset = (page - 1) * per_page

    logs, total = await service.get_all(
        task_id=task_id,
        limit=per_page,
        offset=offset,
    )

    total_pages = ceil(total / per_page) if total > 0 else 1

    return LogListResponse(
        logs=[_log_to_response(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
