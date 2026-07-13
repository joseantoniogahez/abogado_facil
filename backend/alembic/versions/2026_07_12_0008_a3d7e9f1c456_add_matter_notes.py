"""add matter notes

Revision ID: a3d7e9f1c456
Revises: f2c6d8e0b345
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a3d7e9f1c456"
down_revision: str | None = "f2c6d8e0b345"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matter_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_relevant", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(content)) > 0", name="ck_matter_notes_content_not_blank"),
        sa.CheckConstraint("length(content) <= 20000", name="ck_matter_notes_content_max_length"),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matter_notes_firm_id", "matter_notes", ["firm_id"])
    op.create_index("ix_matter_notes_matter_id", "matter_notes", ["matter_id"])
    op.create_index("ix_matter_notes_firm_matter_created", "matter_notes", ["firm_id", "matter_id", "created_at", "id"])


def downgrade() -> None:
    op.drop_index("ix_matter_notes_firm_matter_created", table_name="matter_notes")
    op.drop_index("ix_matter_notes_matter_id", table_name="matter_notes")
    op.drop_index("ix_matter_notes_firm_id", table_name="matter_notes")
    op.drop_table("matter_notes")
