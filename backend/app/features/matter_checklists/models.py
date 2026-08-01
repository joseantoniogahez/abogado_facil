from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class MatterChecklistItem(BaseModel):
    __tablename__ = "matter_checklist_items"
    __table_args__ = (
        Index("ix_matter_checklist_items_firm_matter_position", "firm_id", "matter_id", "position", "id"),
        UniqueConstraint("matter_id", "template_key", name="uq_matter_checklist_items_matter_template"),
        CheckConstraint("status in ('pending', 'complete', 'not_applicable')", name="ck_checklist_item_status"),
        CheckConstraint("length(trim(label)) > 0", name="ck_checklist_item_label_not_blank"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_ai_suggested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    template_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
