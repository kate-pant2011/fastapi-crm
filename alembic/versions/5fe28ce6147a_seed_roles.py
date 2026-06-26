"""seed roles

Revision ID: 5fe28ce6147a
Revises: 20260615152609
Create Date: 2026-06-15 15:31:40.718410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.config.config import now
from sqlalchemy import DateTime, String


# revision identifiers, used by Alembic.
revision: str = '5fe28ce6147a'
down_revision: Union[str, Sequence[str], None] = '20260615152609'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


roles_table = sa.table(
    "roles",
    sa.column("created_at", DateTime),
    sa.column("updated_at", DateTime),
    sa.column("name", String),
)


def upgrade() -> None:
    op.bulk_insert(
        roles_table,
        [
            {
                "created_at": now,
                "updated_at": now,
                "name": "owner",
            },
            {
                "created_at": now,
                "updated_at": now,
                "name": "admin",
            },
            {
                "created_at": now,
                "updated_at": now,
                "name": "manager",
            },
            {
                "created_at": now,
                "updated_at": now,
                "name": "executor",
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM roles WHERE name IN ('owner', 'admin', 'manager', 'executor')"
    )