"""add_gastos_and_cotizaciones_tables

Revision ID: 2ddf6d665aae
Revises: 58573a599256
Create Date: 2025-10-19 09:07:25.611621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ddf6d665aae'
down_revision: Union[str, Sequence[str], None] = '58573a599256'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear tabla gasto
    op.create_table(
        'gasto',
        sa.Column('id_gasto', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=True),
        sa.Column('fecha_gasto', sa.DateTime(), nullable=False),
        sa.Column('concepto', sa.String(length=200), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('metodo_pago', sa.String(length=50), nullable=True),
        sa.Column('numero_factura', sa.String(length=50), nullable=True),
        sa.Column('proveedor', sa.String(length=100), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_gasto')
    )
    op.create_index(op.f('ix_gasto_categoria'), 'gasto', ['categoria'], unique=False)
    op.create_index(op.f('ix_gasto_fecha_gasto'), 'gasto', ['fecha_gasto'], unique=False)
    op.create_index(op.f('ix_gasto_id_gasto'), 'gasto', ['id_gasto'], unique=False)
    
    # Crear tabla cotizacion
    op.create_table(
        'cotizacion',
        sa.Column('id_cotizacion', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=True),
        sa.Column('id_cliente', sa.Integer(), nullable=True),
        sa.Column('numero_cotizacion', sa.String(length=50), nullable=False),
        sa.Column('fecha_cotizacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('descuento', sa.Float(), nullable=True),
        sa.Column('impuestos', sa.Float(), nullable=True),
        sa.Column('total', sa.Float(), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('id_venta_relacionada', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_cliente'], ['cliente.id_cliente'], ),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
        sa.ForeignKeyConstraint(['id_venta_relacionada'], ['venta.id_venta'], ),
        sa.PrimaryKeyConstraint('id_cotizacion'),
        sa.UniqueConstraint('numero_cotizacion')
    )
    op.create_index(op.f('ix_cotizacion_estado'), 'cotizacion', ['estado'], unique=False)
    op.create_index(op.f('ix_cotizacion_fecha_cotizacion'), 'cotizacion', ['fecha_cotizacion'], unique=False)
    op.create_index(op.f('ix_cotizacion_id_cotizacion'), 'cotizacion', ['id_cotizacion'], unique=False)
    
    # Crear tabla detalle_cotizacion
    op.create_table(
        'detalle_cotizacion',
        sa.Column('id_detalle', sa.Integer(), nullable=False),
        sa.Column('id_cotizacion', sa.Integer(), nullable=True),
        sa.Column('id_producto', sa.Integer(), nullable=True),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('precio_unitario', sa.Float(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['id_cotizacion'], ['cotizacion.id_cotizacion'], ),
        sa.ForeignKeyConstraint(['id_producto'], ['producto.id_producto'], ),
        sa.PrimaryKeyConstraint('id_detalle')
    )
    op.create_index(op.f('ix_detalle_cotizacion_id_detalle'), 'detalle_cotizacion', ['id_detalle'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_detalle_cotizacion_id_detalle'), table_name='detalle_cotizacion')
    op.drop_table('detalle_cotizacion')
    op.drop_index(op.f('ix_cotizacion_id_cotizacion'), table_name='cotizacion')
    op.drop_index(op.f('ix_cotizacion_fecha_cotizacion'), table_name='cotizacion')
    op.drop_index(op.f('ix_cotizacion_estado'), table_name='cotizacion')
    op.drop_table('cotizacion')
    op.drop_index(op.f('ix_gasto_id_gasto'), table_name='gasto')
    op.drop_index(op.f('ix_gasto_fecha_gasto'), table_name='gasto')
    op.drop_index(op.f('ix_gasto_categoria'), table_name='gasto')
    op.drop_table('gasto')
