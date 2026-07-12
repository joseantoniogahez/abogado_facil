from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class Client(BaseModel):
    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_clients_firm_full_name", "firm_id", "full_name"),
        Index("ix_clients_firm_phone", "firm_id", "phone"),
        CheckConstraint("phone_country_code = '52'", name="ck_clients_mexico_country_code"),
        CheckConstraint("length(phone) = 10", name="ck_clients_phone_length"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_country_code: Mapped[str] = mapped_column(String(3), nullable=False, default="52", server_default="52")
    phone: Mapped[str] = mapped_column(String(10), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
