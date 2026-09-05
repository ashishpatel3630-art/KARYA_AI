"""add refresh token tracking

Revision ID: cdbd028d2eaa
Revises: 0a1eccc25ba3
Create Date: 2026-09-04 20:37:14.457995
"""

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cdbd028d2eaa"
down_revision: Union[str, Sequence[str], None] = "0a1eccc25ba3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Existing sessions already exist, so these columns must initially
    # allow NULL values while we backfill them.

    op.add_column(
        "sessions",
        sa.Column("jti", sa.String(length=36), nullable=True),
    )

    op.add_column(
        "sessions",
        sa.Column("token_family", sa.String(length=36), nullable=True),
    )

    # Every existing session gets its own unique JTI and token family.
    connection = op.get_bind()

    sessions = connection.execute(
        sa.text("SELECT id FROM sessions WHERE jti IS NULL")
    ).fetchall()

    for (session_id,) in sessions:
        session_jti = str(uuid.uuid4())
        session_family = str(uuid.uuid4())

        connection.execute(
            sa.text(
                """
                UPDATE sessions
                SET jti = :jti,
                    token_family = :token_family
                WHERE id = :session_id
                """
            ),
            {
                "jti": session_jti,
                "token_family": session_family,
                "session_id": session_id,
            },
        )

    # Now that all existing rows have values, enforce NOT NULL.
    op.alter_column(
        "sessions",
        "jti",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    op.alter_column(
        "sessions",
        "token_family",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    # JTI must uniquely identify one refresh-token session.
    op.create_index(
        op.f("ix_sessions_jti"),
        "sessions",
        ["jti"],
        unique=True,
    )

    # Token family is intentionally non-unique because multiple rotated
    # refresh-token sessions belong to the same family.
    op.create_index(
        op.f("ix_sessions_token_family"),
        "sessions",
        ["token_family"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema."""

    op.drop_index(
        op.f("ix_sessions_token_family"),
        table_name="sessions",
    )

    op.drop_index(
        op.f("ix_sessions_jti"),
        table_name="sessions",
    )

    op.drop_column("sessions", "token_family")
    op.drop_column("sessions", "jti")