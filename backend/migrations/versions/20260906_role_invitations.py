"""add trusted role invitations

Revision ID: 20260906_role_invites
Revises: 20260906_reg_creds
Create Date: 2026-09-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260906_role_invites"
down_revision: Union[str, Sequence[str], None] = "20260906_reg_creds"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "role_invitations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_role_invitations_token_hash", "role_invitations", ["token_hash"], unique=True)
    op.create_index("ix_role_invitations_email", "role_invitations", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_role_invitations_email", table_name="role_invitations")
    op.drop_index("ix_role_invitations_token_hash", table_name="role_invitations")
    op.drop_table("role_invitations")
