"""add matter checklists

Revision ID: d6a0b2c4f789
Revises: c5f9a1b3e678
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d6a0b2c4f789"
down_revision: str | None = "c5f9a1b3e678"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matter_checklist_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("is_custom", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("template_key", sa.String(length=120), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status in ('pending', 'complete', 'not_applicable')", name="ck_checklist_item_status"),
        sa.CheckConstraint("length(trim(label)) > 0", name="ck_checklist_item_label_not_blank"),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("matter_id", "template_key", name="uq_matter_checklist_items_matter_template"),
    )
    op.create_index("ix_matter_checklist_items_firm_id", "matter_checklist_items", ["firm_id"])
    op.create_index("ix_matter_checklist_items_matter_id", "matter_checklist_items", ["matter_id"])
    op.create_index(
        "ix_matter_checklist_items_firm_matter_position",
        "matter_checklist_items",
        ["firm_id", "matter_id", "position", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_matter_checklist_items_firm_matter_position", table_name="matter_checklist_items")
    op.drop_index("ix_matter_checklist_items_matter_id", table_name="matter_checklist_items")
    op.drop_index("ix_matter_checklist_items_firm_id", table_name="matter_checklist_items")
    op.drop_table("matter_checklist_items")
