"""merge_multiple_heads

Revision ID: 1c7b90e8bae4
Revises: 20251028_add_core_indexes, 20251107_add_lockout
Create Date: 2025-11-10 10:02:25.281038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c7b90e8bae4'
down_revision: Union[str, Sequence[str], None] = ('20251028_add_core_indexes', '20251107_add_lockout')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
