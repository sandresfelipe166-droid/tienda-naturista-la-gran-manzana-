"""Add audit_log table for compliance tracking.

Revision ID: 000000000001
Revises: 999999999999
Create Date: 2025-10-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000000000001'
down_revision = '999999999999'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add audit_log table."""
    op.create_table(
        'audit_log',
        sa.Column('id_audit', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id_audit')
    )
    op.create_index(op.f('ix_audit_log_timestamp'), 'audit_log', ['timestamp'], unique=False)
    op.create_index(op.f('ix_audit_log_user_id'), 'audit_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_log_action'), 'audit_log', ['action'], unique=False)
    op.create_index(op.f('ix_audit_log_resource_type'), 'audit_log', ['resource_type'], unique=False)
    op.create_index(op.f('ix_audit_log_resource_id'), 'audit_log', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_log_ip_address'), 'audit_log', ['ip_address'], unique=False)


def downgrade() -> None:
    """Remove audit_log table."""
    op.drop_index(op.f('ix_audit_log_ip_address'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_resource_id'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_resource_type'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_action'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_user_id'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_timestamp'), table_name='audit_log')
    op.drop_table('audit_log')
