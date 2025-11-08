"""add core indexes for performance on fk and query fields

Revision ID: 20251028_add_core_indexes
Revises: 
Create Date: 2025-10-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251028_add_core_indexes'
down_revision = '2ddf6d665aae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Producto foreign keys
    op.create_index('ix_producto_id_seccion', 'producto', ['id_seccion'], unique=False)
    op.create_index('ix_producto_id_laboratorio', 'producto', ['id_laboratorio'], unique=False)

    # Lote
    op.create_index('ix_lote_id_producto', 'lote', ['id_producto'], unique=False)
    op.create_index('ix_lote_fecha_vencimiento', 'lote', ['fecha_vencimiento'], unique=False)

    # Entrada
    op.create_index('ix_entrada_id_usuario', 'entrada', ['id_usuario'], unique=False)
    op.create_index('ix_entrada_id_lote', 'entrada', ['id_lote'], unique=False)
    op.create_index('ix_entrada_fecha_entrada', 'entrada', ['fecha_entrada'], unique=False)

    # Salida
    op.create_index('ix_salida_id_usuario', 'salida', ['id_usuario'], unique=False)
    op.create_index('ix_salida_id_lote', 'salida', ['id_lote'], unique=False)
    op.create_index('ix_salida_fecha_salida', 'salida', ['fecha_salida'], unique=False)

    # Venta
    op.create_index('ix_venta_id_usuario', 'venta', ['id_usuario'], unique=False)
    op.create_index('ix_venta_id_cliente', 'venta', ['id_cliente'], unique=False)
    op.create_index('ix_venta_fecha_venta', 'venta', ['fecha_venta'], unique=False)

    # DetalleVenta
    op.create_index('ix_detalle_venta_id_venta', 'detalle_venta', ['id_venta'], unique=False)
    op.create_index('ix_detalle_venta_id_lote', 'detalle_venta', ['id_lote'], unique=False)

    # DetalleCotizacion
    op.create_index('ix_detalle_cotizacion_id_cotizacion', 'detalle_cotizacion', ['id_cotizacion'], unique=False)
    op.create_index('ix_detalle_cotizacion_id_producto', 'detalle_cotizacion', ['id_producto'], unique=False)

    # Alerta
    op.create_index('ix_alerta_id_producto', 'alerta', ['id_producto'], unique=False)
    op.create_index('ix_alerta_id_seccion', 'alerta', ['id_seccion'], unique=False)
    op.create_index('ix_alerta_tipo_alerta', 'alerta', ['tipo_alerta'], unique=False)
    op.create_index('ix_alerta_prioridad', 'alerta', ['prioridad'], unique=False)
    op.create_index('ix_alerta_fecha_creacion', 'alerta', ['fecha_creacion'], unique=False)



def downgrade() -> None:
    # Reverse order drops
    op.drop_index('ix_alerta_fecha_creacion', table_name='alerta')
    op.drop_index('ix_alerta_prioridad', table_name='alerta')
    op.drop_index('ix_alerta_tipo_alerta', table_name='alerta')
    op.drop_index('ix_alerta_id_seccion', table_name='alerta')
    op.drop_index('ix_alerta_id_producto', table_name='alerta')

    op.drop_index('ix_detalle_cotizacion_id_producto', table_name='detalle_cotizacion')
    op.drop_index('ix_detalle_cotizacion_id_cotizacion', table_name='detalle_cotizacion')

    op.drop_index('ix_detalle_venta_id_lote', table_name='detalle_venta')
    op.drop_index('ix_detalle_venta_id_venta', table_name='detalle_venta')

    op.drop_index('ix_venta_fecha_venta', table_name='venta')
    op.drop_index('ix_venta_id_cliente', table_name='venta')
    op.drop_index('ix_venta_id_usuario', table_name='venta')

    op.drop_index('ix_salida_fecha_salida', table_name='salida')
    op.drop_index('ix_salida_id_lote', table_name='salida')
    op.drop_index('ix_salida_id_usuario', table_name='salida')

    op.drop_index('ix_entrada_fecha_entrada', table_name='entrada')
    op.drop_index('ix_entrada_id_lote', table_name='entrada')
    op.drop_index('ix_entrada_id_usuario', table_name='entrada')

    op.drop_index('ix_lote_fecha_vencimiento', table_name='lote')
    op.drop_index('ix_lote_id_producto', table_name='lote')

    op.drop_index('ix_producto_id_laboratorio', table_name='producto')
    op.drop_index('ix_producto_id_seccion', table_name='producto')
