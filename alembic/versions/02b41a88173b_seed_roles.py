"""seed_roles

Revision ID: 02b41a88173b
Revises: baaa79b28e49
Create Date: 2026-02-15 12:11:01.887789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.config.config import now
from sqlalchemy import String, DateTime
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '02b41a88173b'
down_revision: Union[str, Sequence[str], None] = 'baaa79b28e49'
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
