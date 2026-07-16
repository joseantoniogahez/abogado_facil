"""add matter tasks

Revision ID: e7b1c3d5a890
Revises: d6a0b2c4f789
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e7b1c3d5a890"
down_revision: str | None = "d6a0b2c4f789"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matter_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_matter_tasks_title_not_blank"),
        sa.CheckConstraint("length(title) <= 500", name="ck_matter_tasks_title_max_length"),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matter_tasks_firm_id", "matter_tasks", ["firm_id"])
    op.create_index("ix_matter_tasks_matter_id", "matter_tasks", ["matter_id"])
    op.create_index("ix_matter_tasks_firm_completed_due", "matter_tasks", ["firm_id", "completed", "due_date", "id"])
    op.create_index(
        "ix_matter_tasks_firm_matter_completed_due",
        "matter_tasks",
        ["firm_id", "matter_id", "completed", "due_date", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_matter_tasks_firm_matter_completed_due", table_name="matter_tasks")
    op.drop_index("ix_matter_tasks_firm_completed_due", table_name="matter_tasks")
    op.drop_index("ix_matter_tasks_matter_id", table_name="matter_tasks")
    op.drop_index("ix_matter_tasks_firm_id", table_name="matter_tasks")
    op.drop_table("matter_tasks")
