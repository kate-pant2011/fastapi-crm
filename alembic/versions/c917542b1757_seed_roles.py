"""seed_roles

Revision ID: c917542b1757
Revises: f77b7fd46260
Create Date: 2026-02-11 17:20:00.860369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.config.config import now
from sqlalchemy import String, DateTime
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = 'c917542b1757'
down_revision: Union[str, Sequence[str], None] = 'f77b7fd46260'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roles_table = table(
    "roles",
    column("created_at", DateTime),
    column("updated_at", DateTime),
    column("name", String),
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
    op.execute("DELETE FROM roles WHERE role_name IN ('owner', 'admin', 'manager', 'executor')")