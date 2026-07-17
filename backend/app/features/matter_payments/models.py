from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class MatterBilling(BaseModel):
    __tablename__ = "matter_billings"
    __table_args__ = (
        UniqueConstraint("matter_id", name="uq_matter_billings_matter_id"),
        CheckConstraint("agreed_fee >= 0", name="ck_matter_billings_agreed_fee_nonnegative"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), nullable=False, index=True)
    agreed_fee: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class MatterPayment(BaseModel):
    __tablename__ = "matter_payments"
    __table_args__ = (
        Index("ix_matter_payments_firm_matter_date", "firm_id", "matter_id", "paid_on", "id"),
        CheckConstraint("amount > 0", name="ck_matter_payments_amount_positive"),
        CheckConstraint("payment_type in ('advance', 'partial')", name="ck_matter_payments_type"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_type: Mapped[str] = mapped_column(Text, nullable=False)
    paid_on: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
