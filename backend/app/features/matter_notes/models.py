from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class MatterNote(BaseModel):
    __tablename__ = "matter_notes"
    __table_args__ = (
        Index("ix_matter_notes_firm_matter_created", "firm_id", "matter_id", "created_at", "id"),
        CheckConstraint("length(trim(content)) > 0", name="ck_matter_notes_content_not_blank"),
        CheckConstraint("length(content) <= 20000", name="ck_matter_notes_content_max_length"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_relevant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
