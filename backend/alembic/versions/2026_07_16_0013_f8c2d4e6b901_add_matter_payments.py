"""add matter payments

Revision ID: f8c2d4e6b901
Revises: e7b1c3d5a890
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f8c2d4e6b901"
down_revision: str | None = "e7b1c3d5a890"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matter_billings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("agreed_fee", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("agreed_fee >= 0", name="ck_matter_billings_agreed_fee_nonnegative"),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("matter_id", name="uq_matter_billings_matter_id"),
    )
    op.create_index("ix_matter_billings_firm_id", "matter_billings", ["firm_id"])
    op.create_index("ix_matter_billings_matter_id", "matter_billings", ["matter_id"])
    op.create_table(
        "matter_payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("payment_type", sa.Text(), nullable=False),
        sa.Column("paid_on", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_matter_payments_amount_positive"),
        sa.CheckConstraint("payment_type in ('advance', 'partial')", name="ck_matter_payments_type"),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matter_payments_firm_id", "matter_payments", ["firm_id"])
    op.create_index("ix_matter_payments_matter_id", "matter_payments", ["matter_id"])
    op.create_index("ix_matter_payments_firm_matter_date", "matter_payments", ["firm_id", "matter_id", "paid_on", "id"])


def downgrade() -> None:
    op.drop_table("matter_payments")
    op.drop_table("matter_billings")
