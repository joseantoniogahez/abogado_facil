"""Add matters.

Revision ID: f2c6d8e0b345
Revises: e1b5c7d9a234
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f2c6d8e0b345"
down_revision: str | None = "e1b5c7d9a234"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("matter_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("counterparty", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("next_action", sa.String(500)),
        sa.Column("next_action_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status in ('active', 'pending', 'closed')", name="ck_matters_status"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matters_firm_id", "matters", ["firm_id"])
    op.create_index("ix_matters_client_id", "matters", ["client_id"])
    op.create_index("ix_matters_firm_status", "matters", ["firm_id", "status"])
    op.create_index("ix_matters_firm_client", "matters", ["firm_id", "client_id"])


def downgrade() -> None:
    op.drop_table("matters")
