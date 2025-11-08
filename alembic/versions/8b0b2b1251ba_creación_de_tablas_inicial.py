"""Creación de tablas inicial

Revision ID: 8b0b2b1251ba
Revises: 
Create Date: 2025-09-02 20:18:29.226550

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8b0b2b1251ba"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Placeholder: añadir aquí op.create_table(...) si corresponde."""
    pass


def downgrade() -> None:
    """Placeholder para revertir upgrade()."""
    pass
