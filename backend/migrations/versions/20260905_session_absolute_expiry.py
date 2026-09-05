"""add absolute session expiry

Revision ID: 20260905_session_absolute_expiry
Revises: 20260904_full_auth_schema
Create Date: 2026-09-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260905_session_absolute_expiry"
down_revision: Union[str, Sequence[str], None] = "20260904_full_auth_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sessions", "absolute_expires_at")