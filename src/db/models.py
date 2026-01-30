"""SQLAlchemy ORM models."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def utc_now() -> str:
    """Get current UTC time as ISO string."""
    return datetime.utcnow().isoformat()


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Task(Base):
    """Task model for storing automation tasks."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
    headless: Mapped[bool] = mapped_column(Boolean, default=True)
    start_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    telegram_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notify_on_success: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_on_failure: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(String(50), default=utc_now)
    updated_at: Mapped[str] = mapped_column(String(50), default=utc_now, onupdate=utc_now)
    last_run_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    next_run_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    logs: Mapped[list["TaskLog"]] = relationship(
        "TaskLog", back_populates="task", cascade="all, delete-orphan"
    )


class TaskLog(Base):
    """Task execution log model."""

    __tablename__ = "task_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # running, success, failure, timeout
    started_at: Mapped[str] = mapped_column(String(50), nullable=False)
    completed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_steps: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    created_at: Mapped[str] = mapped_column(String(50), default=utc_now)

    task: Mapped["Task"] = relationship("Task", back_populates="logs")
