"""add foreign key constraint to alerta table

Revision ID: 999999999997
Revises: 999999999998
Create Date: 2025-09-07 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '999999999997'
down_revision = '999999999998'
branch_labels = None
depends_on = None


def upgrade():
    # Add foreign key constraint for id_seccion in alerta table
    with op.batch_alter_table('alerta') as batch_op:
        batch_op.create_foreign_key(
            'alerta_id_seccion_fkey',
            'seccion',
            ['id_seccion'],
            ['id_seccion']
        )


def downgrade():
    with op.batch_alter_table('alerta') as batch_op:
        batch_op.drop_constraint('alerta_id_seccion_fkey', type_='foreignkey')
