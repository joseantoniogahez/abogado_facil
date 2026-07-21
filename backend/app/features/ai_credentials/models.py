from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class AiCredential(BaseModel):
    __tablename__ = "ai_credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_ai_credentials_user_provider"),
        Index("ix_ai_credentials_firm_user", "firm_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(64), nullable=False)
