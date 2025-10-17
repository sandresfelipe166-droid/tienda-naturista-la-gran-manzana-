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


class ProductoCreate(ProductoBase):
    id_seccion: int
    id_laboratorio: int
    nombre_producto: str
    estado: EstadoEnum


class ProductoUpdate(ProductoBase):
    id_seccion: Optional[int] = None
    id_laboratorio: Optional[int] = None
    nombre_producto: Optional[str] = None
    estado: Optional[EstadoEnum] = None


# ==========================
# Laboratorios
# ==========================
class LaboratorioBase(BaseModel):
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
