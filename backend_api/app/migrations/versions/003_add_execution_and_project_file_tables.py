"""Skip execution tables - they already exist in database

Revision ID: 003
Revises: 002
Create Date: 2026-02-09 00:00:00.000000

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Tables already exist in database, skipping creation"""
    pass


def downgrade() -> None:
    """No changes to downgrade"""
    pass
