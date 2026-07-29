from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class AIAssistanceResult(BaseModel):
    __tablename__ = "ai_assistance_results"
    __table_args__ = (Index("ix_ai_assistance_results_scope", "firm_id", "matter_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    execution_id: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    feature: Mapped[str] = mapped_column(String(40), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    source_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    generated_content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    reviewed_content: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    problem_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    converted_actions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
