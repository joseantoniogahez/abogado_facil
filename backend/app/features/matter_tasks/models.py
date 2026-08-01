from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class MatterTask(BaseModel):
    __tablename__ = "matter_tasks"
    __table_args__ = (
        Index("ix_matter_tasks_firm_completed_due", "firm_id", "completed", "due_date", "id"),
        Index("ix_matter_tasks_firm_matter_completed_due", "firm_id", "matter_id", "completed", "due_date", "id"),
        CheckConstraint("length(trim(title)) > 0", name="ck_matter_tasks_title_not_blank"),
        CheckConstraint("length(title) <= 500", name="ck_matter_tasks_title_max_length"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
