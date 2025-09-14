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
    # Add missing columns to alerta table if they don't exist
    with op.batch_alter_table('alerta') as batch_op:
        batch_op.add_column(sa.Column('prioridad', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('id_seccion', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('dias_para_vencer', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('stock_actual', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('stock_minimo', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('alerta') as batch_op:
        batch_op.drop_column('prioridad')
        batch_op.drop_column('id_seccion')
        batch_op.drop_column('dias_para_vencer')
        batch_op.drop_column('stock_actual')
        batch_op.drop_column('stock_minimo')
