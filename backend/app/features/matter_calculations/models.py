from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class MatterCalculation(BaseModel):
    __tablename__ = "matter_calculations"
    __table_args__ = (Index("ix_matter_calculations_firm_matter_created", "firm_id", "matter_id", "created_at", "id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True)
    calculation_type: Mapped[str] = mapped_column(Text, nullable=False)
    inputs_json: Mapped[str] = mapped_column(Text, nullable=False)
    result_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
