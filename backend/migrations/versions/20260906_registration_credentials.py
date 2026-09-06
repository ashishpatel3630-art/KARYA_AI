"""add registration identity and secret credential fields

Revision ID: 20260906_registration_credentials
Revises: 89d91bdaa752
Create Date: 2026-09-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260906_reg_creds"
down_revision: Union[str, Sequence[str], None] = "89d91bdaa752"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("secret_key_hash", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "secret_key_hash")
    op.drop_column("users", "name")
