"""restructure all models with relationships

Revision ID: 813e6b3d7b9a
Revises: 8b0b2b1251ba
Create Date: 2025-09-05 21:18:22.120366

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "813e6b3d7b9a"
down_revision: Union[str, Sequence[str], None] = "8b0b2b1251ba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Placeholder: rellena con las operaciones generadas por autogenerate si las tienes."""
    pass


def downgrade() -> None:
    pass