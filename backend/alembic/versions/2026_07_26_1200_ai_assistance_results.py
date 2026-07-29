"""add controlled AI assistance results

Revision ID: 202607261200
Revises: ai_jobs_20260725
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202607261200"
down_revision: str | None = "ai_jobs_20260725"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_assistance_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.String(length=32), nullable=False),
        sa.Column("feature", sa.String(length=40), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("source_version", sa.String(length=64), nullable=False),
        sa.Column("source_snapshot", sa.JSON(), nullable=False),
        sa.Column("generated_content", sa.JSON(), nullable=False),
        sa.Column("reviewed_content", sa.JSON(), nullable=True),
        sa.Column("review_status", sa.String(length=20), nullable=False),
        sa.Column("problem_report", sa.Text(), nullable=True),
        sa.Column("converted_actions", sa.JSON(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("execution_id"),
    )
    op.create_index(
        "ix_ai_assistance_results_scope",
        "ai_assistance_results",
        ["firm_id", "matter_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_assistance_results_scope", table_name="ai_assistance_results")
    op.drop_table("ai_assistance_results")
