from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class AIJob(BaseModel):
    __tablename__ = "ai_jobs"
    __table_args__ = (
        UniqueConstraint("execution_id", name="uq_ai_jobs_execution_id"),
        CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')",
            name="ck_ai_jobs_status",
        ),
        CheckConstraint("attempt_count >= 0", name="ck_ai_jobs_attempt_count"),
        CheckConstraint(
            "(status = 'succeeded' AND result IS NOT NULL AND error_code IS NULL) "
            "OR (status = 'failed' AND result IS NULL AND error_code IS NOT NULL) "
            "OR (status IN ('queued', 'running', 'cancelled') AND result IS NULL AND error_code IS NULL)",
            name="ck_ai_jobs_terminal_payload",
        ),
        Index("ix_ai_jobs_firm_user_created", "firm_id", "user_id", "created_at"),
        Index("ix_ai_jobs_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(32), nullable=False)
    request_id: Mapped[str] = mapped_column(String(100), nullable=False)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    feature: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON(none_as_null=True),
        nullable=True,
        default=None,
    )
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
