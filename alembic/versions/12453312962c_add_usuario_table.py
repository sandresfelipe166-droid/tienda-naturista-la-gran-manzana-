"""add_usuario_table

Revision ID: 12453312962c
Revises: 813e6b3d7b9a
Create Date: 2025-09-06 02:51:49.711715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "12453312962c"
down_revision: Union[str, Sequence[str], None] = "813e6b3d7b9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Placeholder: añadir aquí op.create_table(...) para la tabla usuario si corresponde."""
    pass


def downgrade() -> None:
    pass
