"""merge migration heads

Revision ID: 89d91bdaa752
Revises: 04bcf6494531, 20260905_mfa_recovery_codes
Create Date: 2026-09-05 22:04:16.688742
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89d91bdaa752'
down_revision: Union[str, Sequence[str], None] = ('04bcf6494531', '20260905_mfa_recovery_codes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    pass


def downgrade() -> None:
    """Downgrade database schema."""
    pass
