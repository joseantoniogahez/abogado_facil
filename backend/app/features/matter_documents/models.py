import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class MatterDocument(BaseModel):
    __tablename__ = "matter_documents"
    __table_args__ = (
        Index("ix_matter_documents_firm_matter_created", "firm_id", "matter_id", "created_at", "id"),
        CheckConstraint("size_bytes > 0", name="ck_matter_documents_size_positive"),
        CheckConstraint(
            "text_extraction_status IN ('unprocessed', 'not_applicable', 'available', 'empty', 'failed')",
            name="ck_matter_documents_text_extraction_status",
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    matter_id: Mapped[int] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    text_extraction_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unprocessed")
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
