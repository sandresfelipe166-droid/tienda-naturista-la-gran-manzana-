"""add remaining columns to alerta table

Revision ID: 999999999998
Revises: 999999999999
Create Date: 2025-09-07 14:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '999999999998'
down_revision = '999999999999'
branch_labels = None
depends_on = None


def upgrade():
    # Add remaining missing columns to alerta table
    with op.batch_alter_table('alerta') as batch_op:
        batch_op.add_column(sa.Column('fecha_creacion', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('fecha_resolucion', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('estado', sa.String(length=20), nullable=True, default='Activo'))


def downgrade():
    with op.batch_alter_table('alerta') as batch_op:
        batch_op.drop_column('fecha_creacion')
        batch_op.drop_column('fecha_resolucion')
        batch_op.drop_column('estado')
