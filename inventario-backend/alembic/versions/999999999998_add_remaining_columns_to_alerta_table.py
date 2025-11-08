"""add remaining columns to alerta table

Revision ID: 999999999998
Revises: 999999999999
Create Date: 2025-09-07 14:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Union, Sequence


# revision identifiers, used by Alembic.
revision: str = "999999999998"
down_revision: Union[str, Sequence[str], None] = "999999999999"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Añade columnas faltantes a la tabla alerta de forma segura (batch_alter_table)."""
    with op.batch_alter_table("alerta", schema=None) as batch_op:
        batch_op.add_column(sa.Column("fecha_creacion", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("fecha_resolucion", sa.DateTime(), nullable=True))
        # Para añadir un valor por defecto en PostgreSQL usar server_default
        batch_op.add_column(
            sa.Column(
                "estado",
                sa.String(length=20),
                nullable=True,
                server_default=sa.text("'Activo'")
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("alerta", schema=None) as batch_op:
        batch_op.drop_column("estado")
        batch_op.drop_column("fecha_resolucion")
        batch_op.drop_column("fecha_creacion")
