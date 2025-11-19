"""add foreign key constraint to alerta table

Revision ID: 999999999997
Revises: 999999999998
Create Date: 2025-09-07 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '999999999997'
down_revision = '999999999998'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    fk_name = 'alerta_id_seccion_fkey'
    fk_exists = any(
        fk.get('name') == fk_name
        for fk in inspector.get_foreign_keys('alerta')
    )

    if not fk_exists:
        with op.batch_alter_table('alerta') as batch_op:
            batch_op.create_foreign_key(
                fk_name,
                'seccion',
                ['id_seccion'],
                ['id_seccion']
            )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    fk_name = 'alerta_id_seccion_fkey'
    fk_exists = any(
        fk.get('name') == fk_name
        for fk in inspector.get_foreign_keys('alerta')
    )

    if fk_exists:
        with op.batch_alter_table('alerta') as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')
