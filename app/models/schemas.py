from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar('T')


class EstadoEnum(str, Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    SUSPENDIDO = "Suspendido"


# ==========================
# Alertas
# ==========================
class AlertaBase(BaseModel):
    id_producto: int
    tipo_alerta: str | None = None
    prioridad: str | None = "Media"
    mensaje: str | None = None
    fecha_creacion: datetime
    fecha_resolucion: datetime | None = None
    estado: EstadoEnum | None = EstadoEnum.ACTIVO
    id_seccion: int | None = None
    dias_para_vencer: int | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None

    model_config = ConfigDict(from_attributes=True)


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    tipo_alerta: str | None = None
    prioridad: str | None = None
    mensaje: str | None = None
    fecha_resolucion: datetime | None = None
    estado: EstadoEnum | None = None
    dias_para_vencer: int | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: list[T]
    pagination: dict[str, Any]
    filters_applied: dict[str, Any] | None = None


# Generic simple message response
class MessageResponse(BaseModel):
    success: bool
    message: str


# Inventory summary responses
class InventorySummary(BaseModel):
    total_productos: int
    valor_total_stock: float
    productos_bajo_stock: int


class InventorySummaryResponse(BaseModel):
    success: bool
    message: str
    data: InventorySummary


# Alertas specific responses
class AlertaResponse(BaseModel):
    success: bool
    message: str
    data: AlertaBase


class AlertaId(BaseModel):
    id_alerta: int


class AlertaCreateResponse(BaseModel):
    success: bool
    message: str
    data: AlertaId


# ==========================
# Secciones
# ==========================
class SeccionBase(BaseModel):
    id_seccion: int | None = None
    nombre_seccion: str = Field(..., min_length=1, max_length=100)
    descripcion: str | None = None
    ubicacion_fisica: str | None = Field(None, max_length=100)
    capacidad_maxima: int | None = 0
    temperatura_recomendada: str | None = None
    fecha_ultimo_mantenimiento: datetime | None = None
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class SeccionPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: list[SeccionBase]
    pagination: dict[str, Any]
    filters_applied: dict[str, Any] | None = None


class SeccionResponse(BaseModel):
    success: bool
    message: str
    data: SeccionBase


class SeccionId(BaseModel):
    id_seccion: int


class SeccionCreateResponse(BaseModel):
    success: bool
    message: str
    data: SeccionId


class AlertaPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: list[AlertaBase]
    pagination: dict[str, Any]
    filters_applied: dict[str, Any] | None = None


class SeccionCreate(SeccionBase):
    pass


class SeccionUpdate(BaseModel):
    nombre_seccion: str | None = Field(None, min_length=1, max_length=100)
    descripcion: str | None = None
    ubicacion_fisica: str | None = Field(None, max_length=100)
    capacidad_maxima: int | None = None
    temperatura_recomendada: str | None = None
    fecha_ultimo_mantenimiento: datetime | None = None
    estado: EstadoEnum | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


# ==========================
# Productos
# ==========================
class ProductoBase(BaseModel):
    id_producto: int | None = None
    id_seccion: int | None = None
    id_laboratorio: int | None = None
    nombre_producto: str | None = None
    principio_activo: str | None = None
    concentracion: str | None = None
    forma_farmaceutica: str | None = None
    codigo_barras: str | None = None
    requiere_receta: bool | None = None
    precio_compra: float | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None
    descripcion: str | None = None
    estado: EstadoEnum | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductoPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: list[ProductoBase]
    pagination: dict[str, Any]
    filters_applied: dict[str, Any] | None = None


class ProductoResponse(BaseModel):
    success: bool
    message: str
    data: ProductoBase


class ProductoId(BaseModel):
    id_producto: int


class ProductoCreateResponse(BaseModel):
    success: bool
    message: str
    data: ProductoId


class ProductoCreate(BaseModel):
    id_seccion: int
    id_laboratorio: int
    nombre_producto: str
    principio_activo: str | None = None
    concentracion: str | None = None
    forma_farmaceutica: str | None = None
    codigo_barras: str | None = None
    requiere_receta: bool | None = None
    precio_compra: float | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None
    descripcion: str | None = None
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(from_attributes=True)


class ProductoUpdate(BaseModel):
    id_seccion: int | None = None
    id_laboratorio: int | None = None
    nombre_producto: str | None = None
    principio_activo: str | None = None
    concentracion: str | None = None
    forma_farmaceutica: str | None = None
    codigo_barras: str | None = None
    requiere_receta: bool | None = None
    precio_compra: float | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None
    descripcion: str | None = None
    estado: EstadoEnum | None = None

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Laboratorios
# ==========================
class LaboratorioBase(BaseModel):
    id_laboratorio: int | None = None
    nombre_laboratorio: str = Field(..., min_length=1, max_length=100)
    pais_origen: str | None = Field(None, max_length=100)
    # Sin patrón para lectura/serialización de datos existentes, solo límite de longitud
    telefono: str | None = Field(None, max_length=25)
    email: str | None = Field(None, max_length=254)
    direccion: str | None = Field(None, max_length=200)
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class LaboratorioCreate(LaboratorioBase):
    # En creación permitimos caracteres comunes de teléfono, con longitud
    telefono: str | None = Field(None, max_length=25, pattern=r'^[+0-9()\s-]{7,25}$')
    email: EmailStr | None = None


class LaboratorioUpdate(BaseModel):
    nombre_laboratorio: str | None = Field(None, min_length=1, max_length=100)
    pais_origen: str | None = Field(None, max_length=100)
    telefono: str | None = Field(None, max_length=25, pattern=r'^[+0-9()\s-]{7,25}$')
    email: EmailStr | None = Field(None)
    direccion: str | None = Field(None, max_length=200)
    estado: EstadoEnum | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LaboratorioPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: list[LaboratorioBase]
    pagination: dict[str, Any]
    filters_applied: dict[str, Any] | None = None


class LaboratorioResponse(BaseModel):
    success: bool
    message: str
    data: LaboratorioBase


class LaboratorioId(BaseModel):
    id_laboratorio: int


class LaboratorioCreateResponse(BaseModel):
    success: bool
    message: str
    data: LaboratorioId


# ==========================
# Clientes
# ==========================
class ClienteBase(BaseModel):
    nombre_cliente: str = Field(..., min_length=1, max_length=100)
    apellido_cliente: str = Field(..., min_length=1, max_length=100)
    cedula: str = Field(..., min_length=1, max_length=20)
    telefono: str | None = Field(None, max_length=20, pattern=r'^\+?\d{7,20}$')
    email: EmailStr = Field(...)
    direccion: str | None = Field(None, max_length=200)
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre_cliente: str | None = Field(None, min_length=1, max_length=100)
    apellido_cliente: str | None = Field(None, min_length=1, max_length=100)
    cedula: str | None = Field(None, min_length=1, max_length=20)
    telefono: str | None = Field(None, max_length=20, pattern=r'^\+?\d{7,20}$')
    email: EmailStr | None = None
    direccion: str | None = Field(None, max_length=200)
    estado: EstadoEnum | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


# ==========================
# Roles
# ==========================
class RolResponse(BaseModel):
    id_rol: int
    nombre_rol: str
    descripcion: str | None = None
    permisos: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Users & Auth
# ==========================
class UserBase(BaseModel):
    username: str
    email: EmailStr
    nombre_completo: str | None = None


class UserCreate(UserBase):
    password: str
    rol_id: int


class UserResponse(BaseModel):
    id_usuario: int
    nombre_usuario: str
    email: EmailStr
    nombre_completo: str | None = None
    estado: EstadoEnum
    fecha_creacion: datetime | None = None
    ultima_acceso: datetime | None = None
    id_rol: int
    rol: RolResponse | None = None  # Incluir datos del rol

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    nombre_completo: str | None = None
    estado: EstadoEnum | None = None
    password: str | None = None
    id_rol: int | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    nombre_completo: str | None = None
    rol_id: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    codigo: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ==========================
# Ventas y Detalles
# ==========================
class DetalleVentaBase(BaseModel):
    id_lote: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)
    subtotal: float = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVentaResponse(DetalleVentaBase):
    id_detalle: int
    id_venta: int


class VentaBase(BaseModel):
    id_cliente: int
    fecha_venta: datetime
    subtotal: float = Field(..., ge=0)
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    total: float = Field(..., gt=0)
    metodo_pago: str = Field(..., max_length=50)
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(from_attributes=True)


class VentaCreate(BaseModel):
    id_cliente: int
    fecha_venta: datetime | None = None
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    metodo_pago: str = Field(..., max_length=50)
    detalles: list[DetalleVentaCreate] = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class VentaResponse(VentaBase):
    id_venta: int
    id_usuario: int
    detalles: list[DetalleVentaResponse] | None = []


class VentaUpdate(BaseModel):
    estado: EstadoEnum | None = None

    model_config = ConfigDict(from_attributes=True)


# Estadísticas de Ventas
class VentaEstadisticasMes(BaseModel):
    mes: int  # 1-12
    año: int
    total_ventas: float
    cantidad_ventas: int
    promedio_venta: float


class VentaEstadisticasAño(BaseModel):
    año: int
    total_ventas: float
    cantidad_ventas: int
    meses: list[VentaEstadisticasMes]


# ==========================
# Gastos
# ==========================
class GastoBase(BaseModel):
    fecha_gasto: datetime
    concepto: str = Field(..., min_length=1, max_length=200)
    categoria: str = Field(
        ..., min_length=1, max_length=50
    )  # Compras, Servicios, Mantenimiento, Otros
    monto: float = Field(..., gt=0)
    metodo_pago: str | None = Field(None, max_length=50)
    numero_factura: str | None = Field(None, max_length=50)
    proveedor: str | None = Field(None, max_length=100)
    observaciones: str | None = None
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(from_attributes=True)


class GastoCreate(GastoBase):
    pass


class GastoResponse(GastoBase):
    id_gasto: int
    id_usuario: int


class GastoUpdate(BaseModel):
    concepto: str | None = Field(None, min_length=1, max_length=200)
    categoria: str | None = Field(None, min_length=1, max_length=50)
    monto: float | None = Field(None, gt=0)
    metodo_pago: str | None = Field(None, max_length=50)
    numero_factura: str | None = Field(None, max_length=50)
    proveedor: str | None = Field(None, max_length=100)
    observaciones: str | None = None
    estado: EstadoEnum | None = None

    model_config = ConfigDict(from_attributes=True)


# Estadísticas de Gastos
class GastoEstadisticasMes(BaseModel):
    mes: int
    año: int
    total_gastos: float
    cantidad_gastos: int
    por_categoria: dict[str, float]


class GastoEstadisticasAño(BaseModel):
    año: int
    total_gastos: float
    cantidad_gastos: int
    meses: list[GastoEstadisticasMes]


# ==========================
# Cotizaciones
# ==========================
class DetalleCotizacionBase(BaseModel):
    id_producto: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)
    subtotal: float = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class DetalleCotizacionCreate(DetalleCotizacionBase):
    pass


class DetalleCotizacionResponse(DetalleCotizacionBase):
    id_detalle: int
    id_cotizacion: int


class CotizacionBase(BaseModel):
    id_cliente: int
    numero_cotizacion: str = Field(..., max_length=50)
    fecha_cotizacion: datetime
    fecha_vencimiento: datetime | None = None
    subtotal: float = Field(..., ge=0)
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    total: float = Field(..., gt=0)
    estado: str = Field(
        default="Pendiente", max_length=20
    )  # Pendiente, Aceptada, Rechazada, Convertida
    observaciones: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CotizacionCreate(BaseModel):
    id_cliente: int
    numero_cotizacion: str | None = None  # Se auto-genera si no se provee
    fecha_cotizacion: datetime | None = None
    fecha_vencimiento: datetime | None = None
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    observaciones: str | None = None
    detalles: list[DetalleCotizacionCreate] = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class CotizacionResponse(CotizacionBase):
    id_cotizacion: int
    id_usuario: int
    id_venta_relacionada: int | None = None
    detalles: list[DetalleCotizacionResponse] | None = []


class CotizacionUpdate(BaseModel):
    estado: str | None = None
    fecha_vencimiento: datetime | None = None
    observaciones: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Estadísticas de Cotizaciones
class CotizacionEstadisticas(BaseModel):
    total_cotizaciones: int
    pendientes: int
    aceptadas: int
    rechazadas: int
    convertidas: int
    tasa_conversion: float  # Porcentaje de cotizaciones convertidas a ventas
