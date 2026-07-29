"""Add persistent AI job lifecycle.

Revision ID: ai_jobs_20260725
Revises: ai_credentials_20260720
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ai_jobs_20260725"
down_revision: str | None = "ai_credentials_20260720"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("execution_id", sa.String(length=32), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("feature", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=50), nullable=False),
        sa.Column("schema_version", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("result", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("attempt_count >= 0", name="ck_ai_jobs_attempt_count"),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')",
            name="ck_ai_jobs_status",
        ),
        sa.CheckConstraint(
            "(status = 'succeeded' AND result IS NOT NULL AND error_code IS NULL) "
            "OR (status = 'failed' AND result IS NULL AND error_code IS NOT NULL) "
            "OR (status IN ('queued', 'running', 'cancelled') AND result IS NULL AND error_code IS NULL)",
            name="ck_ai_jobs_terminal_payload",
        ),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("execution_id", name="uq_ai_jobs_execution_id"),
    )
    op.create_index("ix_ai_jobs_firm_user_created", "ai_jobs", ["firm_id", "user_id", "created_at"])
    op.create_index("ix_ai_jobs_status_created", "ai_jobs", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_jobs_status_created", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_firm_user_created", table_name="ai_jobs")
    op.drop_table("ai_jobs")
