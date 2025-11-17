"""Creación de tablas inicial

Revision ID: 8b0b2b1251ba
Revises: 
Create Date: 2025-09-02 20:18:29.226550

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8b0b2b1251ba"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create core tables used by the application.

    This migration replaces the previous placeholder and creates the primary
    tables (rol, usuario, laboratorio, seccion, producto, cliente, lote,
    entrada, salida, venta, detalle_venta, alerta) so that later incremental
    migrations can safely apply deltas.
    """
    # Tabla rol
    op.create_table(
        "rol",
        sa.Column("id_rol", sa.Integer(), nullable=False),
        sa.Column("nombre_rol", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=200), nullable=True),
        sa.Column("permisos", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id_rol"),
    )

    # Tabla laboratorio
    op.create_table(
        "laboratorio",
        sa.Column("id_laboratorio", sa.Integer(), nullable=False),
        sa.Column("nombre_laboratorio", sa.String(length=100), nullable=False),
        sa.Column("pais_origen", sa.String(length=100), nullable=True),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("direccion", sa.String(length=200), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id_laboratorio"),
    )

    # Tabla seccion
    op.create_table(
        "seccion",
        sa.Column("id_seccion", sa.Integer(), nullable=False),
        sa.Column("nombre_seccion", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=200), nullable=True),
        sa.Column("ubicacion_fisica", sa.String(length=100), nullable=True),
        sa.Column("capacidad_maxima", sa.Integer(), nullable=True),
        sa.Column("temperatura_recomendada", sa.String(length=50), nullable=True),
        sa.Column("fecha_ultimo_mantenimiento", sa.DateTime(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id_seccion"),
    )

    # Tabla producto
    op.create_table(
        "producto",
        sa.Column("id_producto", sa.Integer(), nullable=False),
        sa.Column("id_seccion", sa.Integer(), nullable=False),
        sa.Column("id_laboratorio", sa.Integer(), nullable=False),
        sa.Column("nombre_producto", sa.String(length=100), nullable=False),
        sa.Column("principio_activo", sa.String(length=100), nullable=True),
        sa.Column("concentracion", sa.String(length=50), nullable=True),
        sa.Column("forma_farmaceutica", sa.String(length=50), nullable=True),
        sa.Column("codigo_barras", sa.String(length=50), nullable=True),
        sa.Column("requiere_receta", sa.Boolean(), nullable=True),
        sa.Column("precio_compra", sa.Float(), nullable=False),
        sa.Column("stock_actual", sa.Integer(), nullable=True),
        sa.Column("stock_minimo", sa.Integer(), nullable=True),
        sa.Column("descripcion", sa.String(length=200), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["id_seccion"], ["seccion.id_seccion"]),
        sa.ForeignKeyConstraint(["id_laboratorio"], ["laboratorio.id_laboratorio"]),
        sa.PrimaryKeyConstraint("id_producto"),
    )

    # Tabla cliente
    op.create_table(
        "cliente",
        sa.Column("id_cliente", sa.Integer(), nullable=False),
        sa.Column("nombre_cliente", sa.String(length=100), nullable=False),
        sa.Column("apellido_cliente", sa.String(length=100), nullable=False),
        sa.Column("cedula", sa.String(length=20), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("direccion", sa.String(length=200), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id_cliente"),
    )

    # Tabla usuario
    op.create_table(
        "usuario",
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("id_rol", sa.Integer(), nullable=True),
        sa.Column("nombre_usuario", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("nombre_completo", sa.String(length=100), nullable=True),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=True),
        sa.Column("ultima_acceso", sa.DateTime(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.Column("codigo_recuperacion", sa.String(length=10), nullable=True),
        sa.Column("codigo_recuperacion_expiry", sa.DateTime(), nullable=True),
        sa.Column("reset_attempts", sa.Integer(), nullable=True),
        sa.Column("reset_locked_until", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_rol"], ["rol.id_rol"]),
        sa.PrimaryKeyConstraint("id_usuario"),
    )

    # Tabla lote
    op.create_table(
        "lote",
        sa.Column("id_lote", sa.Integer(), nullable=False),
        sa.Column("id_producto", sa.Integer(), nullable=True),
        sa.Column("numero_lote", sa.String(length=50), nullable=True),
        sa.Column("fecha_produccion", sa.DateTime(), nullable=True),
        sa.Column("fecha_vencimiento", sa.DateTime(), nullable=True),
        sa.Column("cantidad_inicial", sa.Integer(), nullable=False),
        sa.Column("cantidad_disponible", sa.Integer(), nullable=False),
        sa.Column("precio_compra_lote", sa.Float(), nullable=False),
        sa.Column("temperatura_almacenamiento", sa.String(length=50), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["id_producto"], ["producto.id_producto"]),
        sa.PrimaryKeyConstraint("id_lote"),
    )

    # Tabla entrada
    op.create_table(
        "entrada",
        sa.Column("id_entrada", sa.Integer(), nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=True),
        sa.Column("id_lote", sa.Integer(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("fecha_entrada", sa.DateTime(), nullable=False),
        sa.Column("precio_compra_unitario", sa.Float(), nullable=False),
        sa.Column("precio_compra_total", sa.Float(), nullable=False),
        sa.Column("numero_factura_compra", sa.String(length=50), nullable=True),
        sa.Column("proveedor", sa.String(length=100), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"]),
        sa.ForeignKeyConstraint(["id_lote"], ["lote.id_lote"]),
        sa.PrimaryKeyConstraint("id_entrada"),
    )

    # Tabla salida
    op.create_table(
        "salida",
        sa.Column("id_salida", sa.Integer(), nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=True),
        sa.Column("id_lote", sa.Integer(), nullable=True),
        sa.Column("tipo_salida", sa.String(length=50), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("fecha_salida", sa.DateTime(), nullable=False),
        sa.Column("motivo", sa.String(length=100), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"]),
        sa.ForeignKeyConstraint(["id_lote"], ["lote.id_lote"]),
        sa.PrimaryKeyConstraint("id_salida"),
    )

    # Tabla venta
    op.create_table(
        "venta",
        sa.Column("id_venta", sa.Integer(), nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=True),
        sa.Column("id_cliente", sa.Integer(), nullable=True),
        sa.Column("fecha_venta", sa.DateTime(), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("descuento", sa.Float(), nullable=True),
        sa.Column("impuestos", sa.Float(), nullable=True),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("metodo_pago", sa.String(length=50), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"]),
        sa.ForeignKeyConstraint(["id_cliente"], ["cliente.id_cliente"]),
        sa.PrimaryKeyConstraint("id_venta"),
    )

    # Tabla detalle_venta
    op.create_table(
        "detalle_venta",
        sa.Column("id_detalle", sa.Integer(), nullable=False),
        sa.Column("id_venta", sa.Integer(), nullable=True),
        sa.Column("id_lote", sa.Integer(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Float(), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["id_venta"], ["venta.id_venta"]),
        sa.ForeignKeyConstraint(["id_lote"], ["lote.id_lote"]),
        sa.PrimaryKeyConstraint("id_detalle"),
    )

    # Tabla alerta
    op.create_table(
        "alerta",
        sa.Column("id_alerta", sa.Integer(), nullable=False),
        sa.Column("id_producto", sa.Integer(), nullable=True),
        sa.Column("tipo_alerta", sa.String(length=50), nullable=True),
        sa.Column("prioridad", sa.String(length=20), nullable=True),
        sa.Column("mensaje", sa.Text(), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.Column("fecha_resolucion", sa.DateTime(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=True),
        sa.Column("id_seccion", sa.Integer(), nullable=True),
        sa.Column("dias_para_vencer", sa.Integer(), nullable=True),
        sa.Column("stock_actual", sa.Integer(), nullable=True),
        sa.Column("stock_minimo", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["id_producto"], ["producto.id_producto"]),
        sa.ForeignKeyConstraint(["id_seccion"], ["seccion.id_seccion"]),
        sa.PrimaryKeyConstraint("id_alerta"),
    )


def downgrade() -> None:
    # Drop in reverse order to respect FK constraints
    op.drop_table("alerta")
    op.drop_table("detalle_venta")
    op.drop_table("venta")
    op.drop_table("salida")
    op.drop_table("entrada")
    op.drop_table("lote")
    op.drop_table("usuario")
    op.drop_table("cliente")
    op.drop_table("producto")
    op.drop_table("seccion")
    op.drop_table("laboratorio")
    op.drop_table("rol")
