from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


# Modelo para Laboratorios
class Laboratorio(Base):
    __tablename__ = "laboratorio"

    id_laboratorio = Column(Integer, primary_key=True, index=True)
    nombre_laboratorio = Column(String(100), nullable=False)
    pais_origen = Column(String(100))
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(200))
    estado = Column(String(20), default="Activo")
    productos = relationship(argument="Producto", back_populates="laboratorio")


# Modelo para Secciones
class Seccion(Base):
    __tablename__ = "seccion"

    id_seccion = Column(Integer, primary_key=True, index=True)
    nombre_seccion = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(200))
    ubicacion_fisica = Column(String(100))
    capacidad_maxima = Column(Integer, default=0)
    temperatura_recomendada = Column(String(50))
    fecha_ultimo_mantenimiento = Column(DateTime)
    estado = Column(String(20), default="Activo")
    productos = relationship(argument="Producto", back_populates="seccion")


# Modelo para Productos
class Producto(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, index=True)
    id_seccion = Column(Integer, ForeignKey("seccion.id_seccion"), nullable=False)
    id_laboratorio = Column(Integer, ForeignKey("laboratorio.id_laboratorio"), nullable=False)
    nombre_producto = Column(String(100), nullable=False, index=True)
    principio_activo = Column(String(100))
    concentracion = Column(String(50))
    forma_farmaceutica = Column(String(50))
    codigo_barras = Column(String(50), unique=True)
    requiere_receta = Column(Boolean, default=False)
    precio_compra = Column(Float, nullable=False)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)
    descripcion = Column(String(200))
    estado = Column(String(20), default="Activo", index=True)
    seccion = relationship(argument="Seccion", back_populates="productos")
    laboratorio = relationship(argument="Laboratorio", back_populates="productos")
    lotes = relationship(argument="Lote", back_populates="producto")


# Modelo para Clientes
class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre_cliente = Column(String(100), nullable=False)
    apellido_cliente = Column(String(100), nullable=False)
    cedula = Column(String(20), nullable=False, unique=True)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(200))
    estado = Column(String(20), default="Activo")
    ventas = relationship(argument="Venta", back_populates="cliente")
    cotizaciones = relationship(argument="Cotizacion", back_populates="cliente")


# Modelo para Usuario
class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"))
    nombre_usuario = Column(String(50), nullable=False, unique=True)
    email = Column(String(100))
    password_hash = Column(String(255))
    nombre_completo = Column(String(100))
    telefono = Column(String(20))
    fecha_creacion = Column(DateTime)
    ultima_acceso = Column(DateTime)
    estado = Column(String(20), default="Activo")
    codigo_recuperacion = Column(String(10), nullable=True)
    codigo_recuperacion_expiry = Column(DateTime, nullable=True)
    reset_attempts = Column(Integer, default=0)
    reset_locked_until = Column(DateTime, nullable=True)
    rol = relationship(argument="Rol", back_populates="usuarios")
    entradas = relationship(argument="Entrada", back_populates="usuario")
    salidas = relationship(argument="Salida", back_populates="usuario")
    ventas = relationship(argument="Venta", back_populates="usuario")
    gastos = relationship(argument="Gasto", back_populates="usuario")
    cotizaciones = relationship(argument="Cotizacion", back_populates="usuario")


# Modelo para Roles
class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), nullable=False)
    descripcion = Column(String(200))
    permisos = Column(Text)
    usuarios = relationship(argument="Usuario", back_populates="rol")


# Modelo para Lotes
class Lote(Base):
    __tablename__ = "lote"

    id_lote = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    numero_lote = Column(String(50))
    fecha_produccion = Column(DateTime)
    fecha_vencimiento = Column(DateTime)
    cantidad_inicial = Column(Integer, nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)
    precio_compra_lote = Column(Float, nullable=False)
    temperatura_almacenamiento = Column(String(50))
    estado = Column(String(20), default="Activo")
    producto = relationship(argument="Producto", back_populates="lotes")
    entradas = relationship(argument="Entrada", back_populates="lote")
    salidas = relationship(argument="Salida", back_populates="lote")
    detalle_ventas = relationship(argument="DetalleVenta", back_populates="lote")


# Modelo para Entradas
class Entrada(Base):
    __tablename__ = "entrada"

    id_entrada = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_lote = Column(Integer, ForeignKey("lote.id_lote"))
    cantidad = Column(Integer, nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    precio_compra_unitario = Column(Float, nullable=False)
    precio_compra_total = Column(Float, nullable=False)
    numero_factura_compra = Column(String(50))
    proveedor = Column(String(100))
    observaciones = Column(Text)
    usuario = relationship(argument="Usuario", back_populates="entradas")
    lote = relationship(argument="Lote", back_populates="entradas")


# Modelo para Salidas
class Salida(Base):
    __tablename__ = "salida"

    id_salida = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_lote = Column(Integer, ForeignKey("lote.id_lote"))
    tipo_salida = Column(String(50))
    cantidad = Column(Integer, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    motivo = Column(String(100))
    observaciones = Column(Text)
    usuario = relationship(argument="Usuario", back_populates="salidas")
    lote = relationship(argument="Lote", back_populates="salidas")


# Modelo para Ventas
class Venta(Base):
    __tablename__ = "venta"

    id_venta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))
    fecha_venta = Column(DateTime, nullable=False)
    subtotal = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0)
    impuestos = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    metodo_pago = Column(String(50))
    estado = Column(String(20), default="Activo")
    usuario = relationship(argument="Usuario", back_populates="ventas")
    cliente = relationship(argument="Cliente", back_populates="ventas")
    detalles = relationship(argument="DetalleVenta", back_populates="venta")


# Modelo para Detalle de Ventas
class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"))
    id_lote = Column(Integer, ForeignKey("lote.id_lote"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    venta = relationship(argument="Venta", back_populates="detalles")
    lote = relationship(argument="Lote", back_populates="detalle_ventas")


# Modelo para Gastos
class Gasto(Base):
    __tablename__ = "gasto"

    id_gasto = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    fecha_gasto = Column(DateTime, nullable=False, index=True)
    concepto = Column(String(200), nullable=False)
    categoria = Column(
        String(50), nullable=False, index=True
    )  # Compras, Servicios, Mantenimiento, Otros
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50))
    numero_factura = Column(String(50))
    proveedor = Column(String(100))
    observaciones = Column(Text)
    estado = Column(String(20), default="Activo")
    usuario = relationship(argument="Usuario", back_populates="gastos")


# Modelo para Cotizaciones
class Cotizacion(Base):
    __tablename__ = "cotizacion"

    id_cotizacion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))
    numero_cotizacion = Column(String(50), unique=True, nullable=False)
    fecha_cotizacion = Column(DateTime, nullable=False, index=True)
    fecha_vencimiento = Column(DateTime)
    subtotal = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0)
    impuestos = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    estado = Column(
        String(20), default="Pendiente", index=True
    )  # Pendiente, Aceptada, Rechazada, Convertida
    observaciones = Column(Text)
    id_venta_relacionada = Column(Integer, ForeignKey("venta.id_venta"))  # Si se convirtió en venta
    usuario = relationship(argument="Usuario", back_populates="cotizaciones")
    cliente = relationship(argument="Cliente", back_populates="cotizaciones")
    detalles = relationship(argument="DetalleCotizacion", back_populates="cotizacion")


# Modelo para Detalle de Cotizaciones
class DetalleCotizacion(Base):
    __tablename__ = "detalle_cotizacion"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_cotizacion = Column(Integer, ForeignKey("cotizacion.id_cotizacion"))
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    cotizacion = relationship(argument="Cotizacion", back_populates="detalles")
    producto = relationship(argument="Producto")


# Modelo para Alertas
class Alerta(Base):
    __tablename__ = "alerta"

    id_alerta = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    tipo_alerta = Column(String(50))
    prioridad = Column(String(20), default="Media")
    mensaje = Column(Text)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_resolucion = Column(DateTime)
    estado = Column(String(20), default="Activo")
    id_seccion = Column(Integer, ForeignKey("seccion.id_seccion"))
    dias_para_vencer = Column(Integer)
    stock_actual = Column(Integer)
    stock_minimo = Column(Integer)
