from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel


class AIResultFeedback(BaseModel):
    __tablename__ = "ai_result_feedback"
    __table_args__ = (
        UniqueConstraint("result_id", "user_id", name="uq_ai_result_feedback_result_user"),
        CheckConstraint(
            "category IN ('useful', 'needs_correction', 'fabricated', 'missing_information')",
            name="ck_ai_result_feedback_category",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    result_id: Mapped[int] = mapped_column(ForeignKey("ai_assistance_results.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
