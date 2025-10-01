"""Merge heads

Revision ID: 2c99e3aaece6
Revises: 12453312962c, 999999999997
Create Date: 2025-09-07 16:53:23.217806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2c99e3aaece6"
down_revision: Union[str, Sequence[str], None] = ("12453312962c", "999999999997")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge revision: normalmente no operaciones, solo marca unión de heads."""
    pass


def downgrade() -> None:
    """En un merge head normalmente no hay downgrade automático."""
    pass
