"""merge_heads_before_gastos_cotizaciones

Revision ID: 58573a599256
Revises: 000000000001, 42e3e64d9fc7
Create Date: 2025-10-19 09:07:17.958669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58573a599256'
down_revision: Union[str, Sequence[str], None] = ('000000000001', '42e3e64d9fc7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
