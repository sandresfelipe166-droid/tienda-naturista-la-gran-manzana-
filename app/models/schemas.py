from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

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
    tipo_alerta: Optional[str] = None
    prioridad: Optional[str] = "Media"
    mensaje: Optional[str] = None
    fecha_creacion: datetime
    fecha_resolucion: Optional[datetime] = None
    estado: Optional[EstadoEnum] = EstadoEnum.ACTIVO
    id_seccion: Optional[int] = None
    dias_para_vencer: Optional[int] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    tipo_alerta: Optional[str] = None
    prioridad: Optional[str] = None
    mensaje: Optional[str] = None
    fecha_resolucion: Optional[datetime] = None
    estado: Optional[EstadoEnum] = None
    dias_para_vencer: Optional[int] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: List[T]
    pagination: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


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
    id_seccion: Optional[int] = None
    nombre_seccion: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    ubicacion_fisica: Optional[str] = Field(None, max_length=100)
    capacidad_maxima: Optional[int] = 0
    temperatura_recomendada: Optional[str] = None
    fecha_ultimo_mantenimiento: Optional[datetime] = None
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class SeccionPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: List[SeccionBase]
    pagination: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


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
    data: List[AlertaBase]
    pagination: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


class SeccionCreate(SeccionBase):
    pass


class SeccionUpdate(BaseModel):
    nombre_seccion: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    ubicacion_fisica: Optional[str] = Field(None, max_length=100)
    capacidad_maxima: Optional[int] = None
    temperatura_recomendada: Optional[str] = None
    fecha_ultimo_mantenimiento: Optional[datetime] = None
    estado: Optional[EstadoEnum] = None

    model_config = ConfigDict(str_strip_whitespace=True)


# ==========================
# Productos
# ==========================
class ProductoBase(BaseModel):
    id_producto: Optional[int] = None
    id_seccion: Optional[int] = None
    id_laboratorio: Optional[int] = None
    nombre_producto: Optional[str] = None
    principio_activo: Optional[str] = None
    concentracion: Optional[str] = None
    forma_farmaceutica: Optional[str] = None
    codigo_barras: Optional[str] = None
    requiere_receta: Optional[bool] = None
    precio_compra: Optional[float] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoEnum] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: List[ProductoBase]
    pagination: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


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
    principio_activo: Optional[str] = None
    concentracion: Optional[str] = None
    forma_farmaceutica: Optional[str] = None
    codigo_barras: Optional[str] = None
    requiere_receta: Optional[bool] = None
    precio_compra: Optional[float] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None
    descripcion: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(from_attributes=True)


class ProductoUpdate(BaseModel):
    id_seccion: Optional[int] = None
    id_laboratorio: Optional[int] = None
    nombre_producto: Optional[str] = None
    principio_activo: Optional[str] = None
    concentracion: Optional[str] = None
    forma_farmaceutica: Optional[str] = None
    codigo_barras: Optional[str] = None
    requiere_receta: Optional[bool] = None
    precio_compra: Optional[float] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoEnum] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================
# Laboratorios
# ==========================
class LaboratorioBase(BaseModel):
    id_laboratorio: Optional[int] = None
    nombre_laboratorio: str = Field(..., min_length=1, max_length=100)
    pais_origen: Optional[str] = Field(None, max_length=100)
    # Sin patrón para lectura/serialización de datos existentes, solo límite de longitud
    telefono: Optional[str] = Field(None, max_length=25)
    email: Optional[str] = Field(None, max_length=254)
    direccion: Optional[str] = Field(None, max_length=200)
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class LaboratorioCreate(LaboratorioBase):
    # En creación permitimos caracteres comunes de teléfono, con longitud
    telefono: Optional[str] = Field(None, max_length=25, pattern=r'^[+0-9()\s-]{7,25}$')
    email: Optional[EmailStr] = None


class LaboratorioUpdate(BaseModel):
    nombre_laboratorio: Optional[str] = Field(None, min_length=1, max_length=100)
    pais_origen: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=25, pattern=r'^[+0-9()\s-]{7,25}$')
    email: Optional[EmailStr] = Field(None)
    direccion: Optional[str] = Field(None, max_length=200)
    estado: Optional[EstadoEnum] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LaboratorioPaginatedResponse(BaseModel):
    success: bool
    message: str
    data: List[LaboratorioBase]
    pagination: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


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
    telefono: Optional[str] = Field(None, max_length=20, pattern=r'^\+?\d{7,20}$')
    email: EmailStr = Field(...)
    direccion: Optional[str] = Field(None, max_length=200)
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre_cliente: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido_cliente: Optional[str] = Field(None, min_length=1, max_length=100)
    cedula: Optional[str] = Field(None, min_length=1, max_length=20)
    telefono: Optional[str] = Field(None, max_length=20, pattern=r'^\+?\d{7,20}$')
    email: Optional[EmailStr] = None
    direccion: Optional[str] = Field(None, max_length=200)
    estado: Optional[EstadoEnum] = None

    model_config = ConfigDict(str_strip_whitespace=True)


# ==========================
# Usuarios y Auth
# ==========================
class UserBase(BaseModel):
    username: str
    email: EmailStr
    nombre_completo: Optional[str] = None


class UserCreate(UserBase):
    password: str
    rol_id: int


class UserResponse(BaseModel):
    id_usuario: int
    nombre_usuario: str
    email: EmailStr
    nombre_completo: Optional[str] = None
    estado: EstadoEnum
    fecha_creacion: Optional[datetime] = None
    ultima_acceso: Optional[datetime] = None
    id_rol: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    estado: Optional[EstadoEnum] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    nombre_completo: Optional[str] = None
    rol_id: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
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
    fecha_venta: Optional[datetime] = None
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    metodo_pago: str = Field(..., max_length=50)
    detalles: List[DetalleVentaCreate] = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class VentaResponse(VentaBase):
    id_venta: int
    id_usuario: int
    detalles: Optional[List[DetalleVentaResponse]] = []


class VentaUpdate(BaseModel):
    estado: Optional[EstadoEnum] = None

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
    meses: List[VentaEstadisticasMes]


# ==========================
# Gastos
# ==========================
class GastoBase(BaseModel):
    fecha_gasto: datetime
    concepto: str = Field(..., min_length=1, max_length=200)
    categoria: str = Field(..., min_length=1, max_length=50)  # Compras, Servicios, Mantenimiento, Otros
    monto: float = Field(..., gt=0)
    metodo_pago: Optional[str] = Field(None, max_length=50)
    numero_factura: Optional[str] = Field(None, max_length=50)
    proveedor: Optional[str] = Field(None, max_length=100)
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.ACTIVO

    model_config = ConfigDict(from_attributes=True)


class GastoCreate(GastoBase):
    pass


class GastoResponse(GastoBase):
    id_gasto: int
    id_usuario: int


class GastoUpdate(BaseModel):
    concepto: Optional[str] = Field(None, min_length=1, max_length=200)
    categoria: Optional[str] = Field(None, min_length=1, max_length=50)
    monto: Optional[float] = Field(None, gt=0)
    metodo_pago: Optional[str] = Field(None, max_length=50)
    numero_factura: Optional[str] = Field(None, max_length=50)
    proveedor: Optional[str] = Field(None, max_length=100)
    observaciones: Optional[str] = None
    estado: Optional[EstadoEnum] = None

    model_config = ConfigDict(from_attributes=True)


# Estadísticas de Gastos
class GastoEstadisticasMes(BaseModel):
    mes: int
    año: int
    total_gastos: float
    cantidad_gastos: int
    por_categoria: Dict[str, float]


class GastoEstadisticasAño(BaseModel):
    año: int
    total_gastos: float
    cantidad_gastos: int
    meses: List[GastoEstadisticasMes]


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
    fecha_vencimiento: Optional[datetime] = None
    subtotal: float = Field(..., ge=0)
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    total: float = Field(..., gt=0)
    estado: str = Field(default="Pendiente", max_length=20)  # Pendiente, Aceptada, Rechazada, Convertida
    observaciones: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CotizacionCreate(BaseModel):
    id_cliente: int
    numero_cotizacion: Optional[str] = None  # Se auto-genera si no se provee
    fecha_cotizacion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    descuento: float = Field(default=0.0, ge=0)
    impuestos: float = Field(default=0.0, ge=0)
    observaciones: Optional[str] = None
    detalles: List[DetalleCotizacionCreate] = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class CotizacionResponse(CotizacionBase):
    id_cotizacion: int
    id_usuario: int
    id_venta_relacionada: Optional[int] = None
    detalles: Optional[List[DetalleCotizacionResponse]] = []


class CotizacionUpdate(BaseModel):
    estado: Optional[str] = None
    fecha_vencimiento: Optional[datetime] = None
    observaciones: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Estadísticas de Cotizaciones
class CotizacionEstadisticas(BaseModel):
    total_cotizaciones: int
    pendientes: int
    aceptadas: int
    rechazadas: int
    convertidas: int
    tasa_conversion: float  # Porcentaje de cotizaciones convertidas a ventas

