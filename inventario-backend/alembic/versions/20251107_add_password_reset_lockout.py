"""add_password_reset_lockout

Revision ID: 20251107_add_lockout
Revises: 20251107_add_password_reset
Create Date: 2025-11-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251107_add_lockout"
down_revision = "20251107_add_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column("reset_attempts", sa.Integer(), default=0, nullable=True),
    )
    op.add_column(
        "usuario",
        sa.Column("reset_locked_until", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usuario", "reset_locked_until")
    op.drop_column("usuario", "reset_attempts")
