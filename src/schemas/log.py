"""Log Pydantic schemas."""
from enum import Enum

from pydantic import BaseModel, Field


class LogStatus(str, Enum):
    """Task log status enum."""

    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class LogResponse(BaseModel):
    """Schema for log response."""

    id: str
    task_id: str
    task_name: str | None = None
    status: LogStatus
    started_at: str
    completed_at: str | None
    duration_seconds: float | None
    result_summary: str | None
    error_message: str | None
    agent_steps: list[dict] | None = Field(default=None)
    created_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class LogListResponse(BaseModel):
    """Schema for log list response."""

    logs: list[LogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
