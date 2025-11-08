"""add_password_reset_columns

Revision ID: 20251107_add_password_reset
Revises: 12453312962c
Create Date: 2025-11-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251107_add_password_reset"
down_revision = "12453312962c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column("codigo_recuperacion", sa.String(length=10), nullable=True),
    )
    op.add_column(
        "usuario",
        sa.Column("codigo_recuperacion_expiry", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usuario", "codigo_recuperacion_expiry")
    op.drop_column("usuario", "codigo_recuperacion")
