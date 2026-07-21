"""Add encrypted BYOK credentials.

Revision ID: ai_credentials_20260720
Revises: e613d73494b2
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ai_credentials_20260720"
down_revision: str | None = "e613d73494b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_credentials",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("encrypted_api_key", sa.Text(), nullable=False),
        sa.Column("nonce", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "provider", name="uq_ai_credentials_user_provider"),
    )
    op.create_index("ix_ai_credentials_firm_user", "ai_credentials", ["firm_id", "user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_credentials_firm_user", table_name="ai_credentials")
    op.drop_table("ai_credentials")
