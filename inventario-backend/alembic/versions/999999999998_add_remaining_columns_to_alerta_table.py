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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("alerta")}

    columns_to_add = [
        sa.Column("fecha_creacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_resolucion", sa.DateTime(), nullable=True),
        sa.Column(
            "estado",
            sa.String(length=20),
            nullable=True,
            server_default=sa.text("'Activo'"),
        ),
    ]

    with op.batch_alter_table("alerta", schema=None) as batch_op:
        for column in columns_to_add:
            if column.name not in existing_columns:
                batch_op.add_column(column)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("alerta")}

    columns_to_drop = [
        "estado",
        "fecha_resolucion",
        "fecha_creacion",
    ]

    with op.batch_alter_table("alerta", schema=None) as batch_op:
        for column_name in columns_to_drop:
            if column_name in existing_columns:
                batch_op.drop_column(column_name)
