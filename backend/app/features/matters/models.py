from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class Matter(BaseModel):
    __tablename__ = "matters"
    __table_args__ = (
        Index("ix_matters_firm_status", "firm_id", "status"),
        Index("ix_matters_firm_client", "firm_id", "client_id"),
        CheckConstraint("status in ('active', 'pending', 'closed')", name="ck_matters_status"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    matter_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    counterparty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(500), nullable=True)
    next_action_date: Mapped[date | None] = mapped_column(Date, nullable=True)
