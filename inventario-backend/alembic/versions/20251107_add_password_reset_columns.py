"""add_password_reset_columns

Revision ID: 20251107_add_password_reset
Revises: 12453312962c
Create Date: 2025-11-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251107_add_password_reset"
down_revision = "12453312962c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("usuario")}

    if "codigo_recuperacion" not in existing_columns:
        op.add_column(
            "usuario",
            sa.Column("codigo_recuperacion", sa.String(length=10), nullable=True),
        )

    if "codigo_recuperacion_expiry" not in existing_columns:
        op.add_column(
            "usuario",
            sa.Column("codigo_recuperacion_expiry", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("usuario")}

    if "codigo_recuperacion_expiry" in existing_columns:
        op.drop_column("usuario", "codigo_recuperacion_expiry")

    # refresh metadata if first drop executed to avoid stale cache
    if "codigo_recuperacion" in existing_columns:
        op.drop_column("usuario", "codigo_recuperacion")
