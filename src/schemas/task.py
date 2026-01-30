"""Task Pydantic schemas."""
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base task schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, description="Natural language task description")
    cron_expression: str | None = Field(default=None, max_length=100, description="Cron expression for scheduled runs. Leave empty for manual-only tasks.")
    timezone: str = Field(default="UTC", max_length=50)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    headless: bool = Field(default=True)
    start_url: str | None = Field(default=None, max_length=2048)
    telegram_enabled: bool = Field(default=True)
    telegram_chat_id: str | None = Field(default=None, max_length=100)
    notify_on_success: bool = Field(default=False)
    notify_on_failure: bool = Field(default=True)


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    cron_expression: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=50)
    is_enabled: bool | None = None
    timeout_seconds: int | None = Field(default=None, ge=30, le=3600)
    headless: bool | None = None
    start_url: str | None = Field(default=None, max_length=2048)
    telegram_enabled: bool | None = None
    telegram_chat_id: str | None = Field(default=None, max_length=100)
    notify_on_success: bool | None = None
    notify_on_failure: bool | None = None


class TaskResponse(TaskBase):
    """Schema for task response."""

    id: str
    is_enabled: bool
    created_at: str
    updated_at: str
    last_run_at: str | None
    next_run_at: str | None

    class Config:
        """Pydantic config."""

        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
    total: int
