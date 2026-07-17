"""add matter calculations"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a9d3e5f7c012"
down_revision: str | None = "f8c2d4e6b901"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matter_calculations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("firm_id", sa.Integer(), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("matter_id", sa.Integer(), sa.ForeignKey("matters.id"), nullable=False),
        sa.Column("calculation_type", sa.Text(), nullable=False),
        sa.Column("inputs_json", sa.Text(), nullable=False),
        sa.Column("result_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_matter_calculations_firm_id", "matter_calculations", ["firm_id"])
    op.create_index("ix_matter_calculations_matter_id", "matter_calculations", ["matter_id"])
    op.create_index(
        "ix_matter_calculations_firm_matter_created",
        "matter_calculations",
        ["firm_id", "matter_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_table("matter_calculations")
