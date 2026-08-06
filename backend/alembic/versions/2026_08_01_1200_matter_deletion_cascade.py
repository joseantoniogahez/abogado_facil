"""cascade matter deletion to dependent records

Revision ID: matter_delete_20260801
Revises: ai_checklist_20260731
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "matter_delete_20260801"
down_revision: str | None = "ai_checklist_20260731"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES: tuple[str, ...] = (
    "ai_assistance_results",
    "matter_billings",
    "matter_calculations",
    "matter_checklist_items",
    "matter_documents",
    "matter_notes",
    "matter_payments",
    "matter_tasks",
)


def _replace_foreign_keys(*, ondelete: str | None) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        naming_convention = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}
        for table_name in _TABLES:
            with op.batch_alter_table(table_name, naming_convention=naming_convention) as batch_op:
                batch_op.drop_constraint(f"fk_{table_name}_matter_id_matters", type_="foreignkey")
                batch_op.create_foreign_key(
                    f"fk_{table_name}_matter_id_matters",
                    "matters",
                    ["matter_id"],
                    ["id"],
                    ondelete=ondelete,
                )
        return

    inspector = sa.inspect(bind)
    for table_name in _TABLES:
        constraint_name = next(
            foreign_key["name"]
            for foreign_key in inspector.get_foreign_keys(table_name)
            if foreign_key["constrained_columns"] == ["matter_id"] and foreign_key["referred_table"] == "matters"
        )
        if constraint_name is None:
            raise RuntimeError(f"Matter foreign key on {table_name} must be named")
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")
        op.create_foreign_key(
            constraint_name,
            table_name,
            "matters",
            ["matter_id"],
            ["id"],
            ondelete=ondelete,
        )


def upgrade() -> None:
    _replace_foreign_keys(ondelete="CASCADE")


def downgrade() -> None:
    _replace_foreign_keys(ondelete=None)
