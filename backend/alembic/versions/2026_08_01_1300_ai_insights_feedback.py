"""add structured AI result feedback

Revision ID: ai_insights_20260801
Revises: matter_delete_20260801
"""

import sqlalchemy as sa
from alembic import op

revision = "ai_insights_20260801"
down_revision = "matter_delete_20260801"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_result_feedback",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("result_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "category IN ('useful', 'needs_correction', 'fabricated', 'missing_information')",
            name="ck_ai_result_feedback_category",
        ),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["result_id"], ["ai_assistance_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("result_id", "user_id", name="uq_ai_result_feedback_result_user"),
    )
    op.create_index("ix_ai_result_feedback_firm_id", "ai_result_feedback", ["firm_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_result_feedback_firm_id", table_name="ai_result_feedback")
    op.drop_table("ai_result_feedback")
