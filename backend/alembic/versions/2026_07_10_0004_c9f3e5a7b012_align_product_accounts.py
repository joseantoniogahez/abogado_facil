"""Align authentication with product accounts.

Revision ID: c9f3e5a7b012
Revises: b8e2d4f6a901
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c9f3e5a7b012"
down_revision: str | None = "b8e2d4f6a901"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "firms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint("users_username_key", "users", type_="unique")
    op.drop_column("users", "username")
    op.drop_column("users", "tenant_id")
    op.add_column("users", sa.Column("email", sa.String(length=320), nullable=False))
    op.add_column("users", sa.Column("first_name", sa.String(length=100), nullable=False))
    op.add_column("users", sa.Column("middle_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=False))
    op.add_column("users", sa.Column("display_name", sa.String(length=255), nullable=False))
    op.add_column("users", sa.Column("firm_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_foreign_key("fk_users_firm_id_firms", "users", "firms", ["firm_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_users_firm_id_firms", "users", type_="foreignkey")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_column("users", "firm_id")
    op.drop_column("users", "display_name")
    op.drop_column("users", "last_name")
    op.drop_column("users", "middle_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "email")
    op.add_column("users", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("username", sa.String(length=255), nullable=False))
    op.create_unique_constraint("users_username_key", "users", ["username"])
    op.drop_table("firms")
