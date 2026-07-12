"""Add firm-scoped clients.

Revision ID: d0a4f6b8c123
Revises: c9f3e5a7b012
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d0a4f6b8c123"
down_revision: str | None = "c9f3e5a7b012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(32), nullable=False),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clients_firm_id", "clients", ["firm_id"])
    op.create_index("ix_clients_firm_full_name", "clients", ["firm_id", "full_name"])
    op.create_index("ix_clients_firm_phone", "clients", ["firm_id", "phone"])


def downgrade() -> None:
    op.drop_index("ix_clients_firm_phone", table_name="clients")
    op.drop_index("ix_clients_firm_full_name", table_name="clients")
    op.drop_index("ix_clients_firm_id", table_name="clients")
    op.drop_table("clients")
