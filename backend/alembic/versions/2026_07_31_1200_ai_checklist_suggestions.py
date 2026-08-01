"""mark AI-suggested checklist items

Revision ID: ai_checklist_20260731
Revises: 202607261200
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ai_checklist_20260731"
down_revision: str | None = "202607261200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "matter_checklist_items",
        sa.Column("is_ai_suggested", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("matter_checklist_items", "is_ai_suggested")
