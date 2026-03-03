"""seed_roles

Revision ID: 20260228140415
Revises: 20260228140316
Create Date: 2026-02-28 14:04:16.517661

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.config.config import now
from sqlalchemy import DateTime, String

# revision identifiers, used by Alembic.
revision: str = "20260228140415"
down_revision: Union[str, Sequence[str], None] = "20260228140316"
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
