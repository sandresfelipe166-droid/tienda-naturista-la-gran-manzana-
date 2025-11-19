"""add missing columns to alerta table

Revision ID: 999999999999
Revises: 813e6b3d7b9a
Create Date: 2025-09-07 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '999999999999'
down_revision = '813e6b3d7b9a'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col['name'] for col in inspector.get_columns('alerta')}

    columns_to_add = [
        sa.Column('prioridad', sa.String(length=20), nullable=True),
        sa.Column('id_seccion', sa.Integer(), nullable=True),
        sa.Column('dias_para_vencer', sa.Integer(), nullable=True),
        sa.Column('stock_actual', sa.Integer(), nullable=True),
        sa.Column('stock_minimo', sa.Integer(), nullable=True),
    ]

    with op.batch_alter_table('alerta') as batch_op:
        for column in columns_to_add:
            if column.name not in existing_columns:
                batch_op.add_column(column)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col['name'] for col in inspector.get_columns('alerta')}

    columns_to_drop = [
        'prioridad',
        'id_seccion',
        'dias_para_vencer',
        'stock_actual',
        'stock_minimo',
    ]

    with op.batch_alter_table('alerta') as batch_op:
        for column_name in columns_to_drop:
            if column_name in existing_columns:
                batch_op.drop_column(column_name)
