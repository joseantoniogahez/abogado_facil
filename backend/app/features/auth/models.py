from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class Firm(BaseModel):
    __tablename__ = "firms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, default="Technical")
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, default="User")
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Technical user")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    firm_id: Mapped[int | None] = mapped_column(ForeignKey("firms.id"), nullable=True, default=None)
